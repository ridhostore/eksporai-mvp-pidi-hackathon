# utils/api_server.py
"""
REST API Server untuk EksporAI
FastAPI endpoints untuk UMKM, Buyer, Transactions, Analytics
"""
from fastapi import FastAPI, HTTPException, File, UploadFile, Depends
from pydantic import BaseModel
from typing import List, Optional
from utils.ai_engine import predict_readiness_score
from utils.matchmaking import get_buyer_recommendations
from utils.firebase_config import get_firebase
from utils.transaction_tracker import get_transaction_tracker
from utils.admin_manager import get_admin_manager
from utils.document_processor import process_document_file
from datetime import datetime
import io

# Pydantic Models
class UMKMData(BaseModel):
    """UMKM data model"""
    tahun_berdiri: int
    modal_usaha: float
    omzet_bulanan: float
    jumlah_karyawan: int
    punya_sertifikat_halal: int
    punya_sertifikat_bpom: int
    punya_nib: int
    ekspor_sebelumnya: int
    kapasitas_produksi: float
    sektor: str


class ScoreResponse(BaseModel):
    """Score prediction response"""
    umkm_id: str
    score: int
    status: str
    confidence: float
    recommendations: List[str]


class TransactionData(BaseModel):
    """Transaction data model"""
    umkm_id: str
    buyer_id: str
    quantity: int
    product: str
    value_usd: float
    value_idr: float
    notes: str = ""


class BuyerProfile(BaseModel):
    """Buyer profile model"""
    buyer_id: str
    nama: str
    negara: str
    jenis_perusahaan: str
    deskripsi: str
    min_score: int


# Initialize FastAPI app
app = FastAPI(
    title="EksporAI API",
    description="REST API untuk Platform Ekspor UMKM",
    version="1.0.0"
)

# Get instances
db = get_firebase()
tracker = get_transaction_tracker()
admin = get_admin_manager()


# ===== UMKM Endpoints =====
@app.post("/api/v1/umkm/score", response_model=ScoreResponse)
async def calculate_umkm_score(umkm_data: UMKMData):
    """
    Calculate export readiness score untuk UMKM
    
    Returns:
    - score: 0-100
    - status: "READY", "IMPROVING", "NOT_READY"
    - recommendations: List of suggestions
    """
    try:
        data_dict = umkm_data.dict()
        score = predict_readiness_score(data_dict)
        
        # Determine status
        if score >= 80:
            status = "READY"
        elif score >= 60:
            status = "IMPROVING"
        else:
            status = "NOT_READY"
        
        # Get recommendations
        recommendations = get_buyer_recommendations(
            score, 
            umkm_data.sektor, 
            data_dict,
            top_n=3
        )
        recommendation_names = [b['nama'] for b in recommendations]
        
        return ScoreResponse(
            umkm_id="UMKM_" + str(datetime.now().timestamp()).replace(".", ""),
            score=score,
            status=status,
            confidence=0.92,
            recommendations=recommendation_names
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/umkm/{umkm_id}")
async def get_umkm_profile(umkm_id: str):
    """Get UMKM profile"""
    data = db.get_umkm(umkm_id)
    if not data:
        raise HTTPException(status_code=404, detail="UMKM not found")
    return data


@app.post("/api/v1/umkm/{umkm_id}")
async def update_umkm_profile(umkm_id: str, umkm_data: UMKMData):
    """Update UMKM profile"""
    try:
        db.add_umkm(umkm_id, umkm_data.dict())
        return {"status": "success", "message": "UMKM profile updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== Matchmaking Endpoints =====
@app.get("/api/v1/matchmaking/{umkm_id}")
async def get_buyer_matches(umkm_id: str, limit: int = 5):
    """Get buyer recommendations untuk UMKM"""
    try:
        umkm_data = db.get_umkm(umkm_id)
        if not umkm_data:
            raise HTTPException(status_code=404, detail="UMKM not found")
        
        recommendations = get_buyer_recommendations(
            umkm_data.get('skor_kesiapan', 0),
            umkm_data.get('sektor', 'Makanan'),
            umkm_data,
            top_n=limit
        )
        
        return {
            "umkm_id": umkm_id,
            "total_matches": len(recommendations),
            "buyers": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== Transaction Endpoints =====
@app.post("/api/v1/transactions")
async def create_transaction(trans_data: TransactionData):
    """Create new transaction"""
    try:
        trans_id = tracker.create_transaction(
            trans_data.umkm_id,
            trans_data.buyer_id,
            {
                'quantity': trans_data.quantity,
                'product': trans_data.product,
                'value_usd': trans_data.value_usd,
                'value_idr': trans_data.value_idr,
                'notes': trans_data.notes
            }
        )
        
        return {
            "transaction_id": trans_id,
            "status": "created",
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/transactions/{umkm_id}")
async def get_transaction_history(umkm_id: str, limit: int = 20):
    """Get transaction history untuk UMKM"""
    try:
        transactions = tracker.get_transaction_history(umkm_id, limit)
        stats = tracker.get_transaction_stats(umkm_id)
        
        return {
            "umkm_id": umkm_id,
            "total_transactions": len(transactions),
            "statistics": stats,
            "transactions": transactions
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/v1/transactions/{transaction_id}")
async def update_transaction_status(transaction_id: str, status: str, notes: str = ""):
    """Update transaction status"""
    try:
        success = tracker.update_transaction_status(transaction_id, status, notes)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        return {
            "transaction_id": transaction_id,
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== Admin Endpoints =====
@app.get("/api/v1/admin/dashboard")
async def get_admin_dashboard():
    """Get admin dashboard analytics"""
    try:
        analytics = admin.get_dashboard_analytics()
        system_stats = admin.get_system_stats()
        
        return {
            "analytics": analytics,
            "system_stats": system_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/admin/umkm/list")
async def get_all_umkm():
    """Get list of all UMKM"""
    try:
        df = admin.get_all_umkm()
        return {
            "total": len(df),
            "umkm": df.to_dict('records') if not df.empty else []
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/admin/transactions/analytics")
async def get_transaction_analytics(days: int = 30):
    """Get transaction analytics"""
    try:
        analytics = admin.get_transaction_analytics(days)
        return {
            "period_days": days,
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/admin/buyers")
async def add_buyer(buyer: BuyerProfile):
    """Add new buyer"""
    try:
        success = admin.add_buyer_profile(buyer.buyer_id, buyer.dict())
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add buyer")
        
        return {
            "buyer_id": buyer.buyer_id,
            "status": "created",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== Document Processing Endpoints =====
@app.post("/api/v1/documents/process")
async def process_document(file: UploadFile = File(...)):
    """Process uploaded document (PDF/Image) dan extract UMKM data"""
    try:
        result = process_document_file(file)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== Health Check =====
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
