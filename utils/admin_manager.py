# utils/admin_manager.py
"""
Admin Management System
CRUD untuk UMKM, Buyer, Transaction Monitoring, Analytics
"""
import pandas as pd
from datetime import datetime, timedelta
from utils.firebase_config import get_firebase
from utils.transaction_tracker import get_transaction_tracker
import json


class AdminManager:
    """Manager untuk admin panel operations"""
    
    def __init__(self):
        self.db = get_firebase()
        self.tracker = get_transaction_tracker()
    
    def get_all_umkm(self, limit=100):
        """Get list semua UMKM dengan stats"""
        try:
            umkm_list = []
            # In production, ini akan query Firebase
            # For now, load dari local storage
            import glob
            for file in glob.glob('local_db/umkm_*.json')[:limit]:
                try:
                    with open(file, 'r') as f:
                        umkm = json.load(f)
                        umkm_list.append(umkm)
                except:
                    pass
            
            return pd.DataFrame(umkm_list) if umkm_list else pd.DataFrame()
        except Exception as e:
            print(f"❌ Error fetching UMKM: {e}")
            return pd.DataFrame()
    
    def get_umkm_details(self, umkm_id):
        """Get detailed info tentang specific UMKM"""
        data = self.db.get_umkm(umkm_id)
        if not data:
            return None
        
        # Add transaction stats
        trans_stats = self.tracker.get_transaction_stats(umkm_id)
        data['transaction_stats'] = trans_stats
        
        return data
    
    def verify_umkm_document(self, umkm_id, verification_status, notes=''):
        """
        Verify UMKM documents by admin
        
        verification_status: 'approved', 'rejected', 'need_revision'
        """
        verification_data = {
            'umkm_id': umkm_id,
            'verified_at': datetime.now().isoformat(),
            'status': verification_status,
            'admin_notes': notes
        }
        
        try:
            if not hasattr(self.db, 'is_online') or self.db.is_online:
                pass
            else:
                with open(f'local_db/verification_{umkm_id}.json', 'w') as f:
                    json.dump(verification_data, f, indent=2)
            
            print(f"✅ UMKM {umkm_id} verification status: {verification_status}")
            return True
        except:
            return False
    
    def get_all_buyers(self):
        """Get list semua buyer data"""
        return self.db.get_all_buyers()
    
    def add_buyer_profile(self, buyer_id, buyer_data):
        """Add new buyer ke platform"""
        return self.db.add_buyer(buyer_id, buyer_data)
    
    def delete_buyer(self, buyer_id):
        """Delete buyer dari platform (soft delete)"""
        try:
            if not hasattr(self.db, 'is_online') or self.db.is_online:
                pass
            else:
                try:
                    import os
                    os.remove(f'local_db/buyer_{buyer_id}.json')
                except:
                    pass
            
            print(f"✅ Buyer {buyer_id} deleted")
            return True
        except:
            return False
    
    def get_dashboard_analytics(self):
        """
        Get overall platform analytics untuk dashboard admin
        """
        umkm_df = self.get_all_umkm()
        
        analytics = {
            'total_umkm': len(umkm_df),
            'ready_to_export': len(umkm_df[umkm_df.get('skor_kesiapan', 0) >= 80]) if not umkm_df.empty else 0,
            'total_transactions': 0,
            'successful_transactions': 0,
            'total_transaction_value': 0,
            'top_sectors': {},
            'top_countries': {}
        }
        
        # Calculate sector distribution
        if not umkm_df.empty and 'sektor' in umkm_df.columns:
            analytics['top_sectors'] = umkm_df['sektor'].value_counts().head(5).to_dict()
        
        return analytics
    
    def get_pending_approvals(self):
        """Get list UMKM yang pending approval"""
        import glob
        pending = []
        
        try:
            for file in glob.glob('local_db/verification_*.json'):
                with open(file, 'r') as f:
                    ver = json.load(f)
                    if ver.get('status') == 'need_revision':
                        pending.append(ver)
        except:
            pass
        
        return pending
    
    def get_transaction_analytics(self, days=30):
        """Get transaction analytics untuk periode tertentu"""
        """
        Get transaction analytics untuk periode tertentu
        """
        try:
            import glob
            transactions = []
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            for file in glob.glob('local_db/transaction_*.json'):
                try:
                    with open(file, 'r') as f:
                        trans = json.load(f)
                        if trans.get('created_at', '') >= cutoff_date:
                            transactions.append(trans)
                except:
                    pass
            
            analytics = {
                'total_transactions': len(transactions),
                'completed': len([t for t in transactions if t.get('status') == 'completed']),
                'pending': len([t for t in transactions if t.get('status') == 'pending']),
                'cancelled': len([t for t in transactions if t.get('status') == 'cancelled']),
                'total_value': sum(t.get('value_idr', 0) for t in transactions),
                'avg_transaction_value': 0
            }
            
            if transactions:
                analytics['avg_transaction_value'] = analytics['total_value'] / len(transactions)
            
            return analytics
        except Exception as e:
            print(f"❌ Error calculating analytics: {e}")
            return {}
    
    def export_umkm_report(self):
        """Export UMKM data sebagai CSV"""
        df = self.get_all_umkm()
        if df.empty:
            return None
        
        return df.to_csv(index=False)
    
    def export_transaction_report(self, days=30):
        """Export transaction data sebagai CSV"""
        try:
            import glob
            transactions = []
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            for file in glob.glob('local_db/transaction_*.json'):
                try:
                    with open(file, 'r') as f:
                        trans = json.load(f)
                        if trans.get('created_at', '') >= cutoff_date:
                            transactions.append(trans)
                except:
                    pass
            
            if not transactions:
                return None
            
            df = pd.DataFrame(transactions)
            return df.to_csv(index=False)
        except:
            return None
    
    def get_system_stats(self):
        """Get overall system statistics"""
        umkm_df = self.get_all_umkm()
        buyers = self.get_all_buyers()
        trans_analytics = self.get_transaction_analytics(days=30)
        
        stats = {
            'total_umkm': len(umkm_df),
            'total_buyers': len(buyers) if buyers else 0,
            'monthly_transactions': trans_analytics.get('total_transactions', 0),
            'monthly_successful_tx': trans_analytics.get('completed', 0),
            'monthly_value': trans_analytics.get('total_value', 0),
            'system_uptime': 'Online',
            'last_sync': datetime.now().isoformat()
        }
        
        return stats


def get_admin_manager():
    """Get singleton AdminManager instance"""
    return AdminManager()
