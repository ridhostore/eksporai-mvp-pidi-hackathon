# utils/firebase_config.py
"""
Firebase Configuration & Database Management
Handles Auth, Realtime Database, dan Cloud Storage
"""
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
import os
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FirebaseDB:
    """Singleton Firebase Database Handler"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseDB, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inisialisasi Firebase Admin SDK"""
        try:
            # Check jika Firebase sudah diinisialisasi
            firebase_admin.get_app()
        except ValueError:
            # Jika belum, gunakan .env atau credentials.json
            firebase_key = os.getenv('FIREBASE_KEY')
            
            if firebase_key:
                try:
                    cred = credentials.Certificate(json.loads(firebase_key))
                except:
                    cred = credentials.Certificate('firebase-key.json')
            else:
                # Fallback ke firebase-key.json jika ada
                if os.path.exists('firebase-key.json'):
                    cred = credentials.Certificate('firebase-key.json')
                else:
                    print("❌ Firebase credentials tidak ditemukan")
                    print("Menggunakan mode offline (local storage)")
                    self.is_online = False
                    return
            
            try:
                firebase_admin.initialize_app(cred, {
                    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', '')
                })
                # Initialize Firestore client
                self.db = firestore.client()
                self.is_online = True
            except Exception as e:
                print(f"⚠️ Firebase online mode error: {e}")
                print("Mode fallback ke local storage")
                self.is_online = False
    
    def add_umkm(self, umkm_id, umkm_data):
        """Tambah UMKM profile ke Firestore"""
        if not self.is_online:
            return self._local_add_umkm(umkm_id, umkm_data)
        
        try:
            umkm_data['created_at'] = datetime.now().isoformat()
            umkm_data['last_updated'] = datetime.now().isoformat()
            self.db.collection('umkm').document(umkm_id).set(umkm_data)
            print(f"✅ UMKM {umkm_id} disimpan ke Firestore")
            return True
        except Exception as e:
            print(f"❌ Error saving UMKM: {e}")
            return False
    
    def get_umkm(self, umkm_id):
        """Ambil UMKM profile dari Firestore"""
        if not self.is_online:
            return self._local_get_umkm(umkm_id)
        
        try:
            doc = self.db.collection('umkm').document(umkm_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"❌ Error fetching UMKM: {e}")
            return None
    
    def update_score(self, umkm_id, score, status):
        """Update skor kesiapan UMKM di Firestore"""
        if not self.is_online:
            return self._local_update_score(umkm_id, score, status)
        
        try:
            self.db.collection('umkm').document(umkm_id).update({
                'skor_kesiapan': score,
                'status_ekspor': status,
                'last_updated': datetime.now().isoformat()
            })
            print(f"✅ Skor UMKM {umkm_id} diperbarui di Firestore")
            return True
        except Exception as e:
            print(f"❌ Error updating score: {e}")
            return False
    
    def add_transaction(self, transaction_data):
        """Catat transaksi UMKM-Buyer di Firestore"""
        if not self.is_online:
            return self._local_add_transaction(transaction_data)
        
        try:
            transaction_data['created_at'] = datetime.now().isoformat()
            transaction_data['status'] = 'pending'
            # Firestore akan generate auto ID
            doc_ref = self.db.collection('transactions').add(transaction_data)
            print(f"✅ Transaksi {doc_ref[1].id} dicatat di Firestore")
            return doc_ref[1].id
        except Exception as e:
            print(f"❌ Error recording transaction: {e}")
            return None
            print(f"❌ Error recording transaction: {e}")
            return None
    
    def get_transactions(self, umkm_id, limit=10):
        """Ambil history transaksi UMKM dari Firestore"""
        if not self.is_online:
            return self._local_get_transactions(umkm_id, limit)
        
        try:
            # Simplified query untuk MVP - tanpa composite index requirement
            docs = self.db.collection('transactions').where('umkm_id', '==', umkm_id).limit(limit).stream()
            transactions = []
            for doc in docs:
                trans_data = doc.to_dict()
                trans_data['id'] = doc.id
                transactions.append(trans_data)
            # Sort by created_at descending manually
            transactions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return transactions
        except Exception as e:
            print(f"❌ Error fetching transactions: {e}")
            return []
    
    def add_buyer(self, buyer_id, buyer_data):
        """Tambah buyer profile ke Firestore"""
        if not self.is_online:
            return self._local_add_buyer(buyer_id, buyer_data)
        
        try:
            buyer_data['created_at'] = datetime.now().isoformat()
            self.db.collection('buyers').document(buyer_id).set(buyer_data)
            print(f"✅ Buyer {buyer_id} ditambahkan ke Firestore")
            return True
        except Exception as e:
            print(f"❌ Error adding buyer: {e}")
            return False
    
    def get_all_buyers(self):
        """Ambil semua buyer dari Firestore"""
        if not self.is_online:
            return self._local_get_all_buyers()
        
        try:
            docs = self.db.collection('buyers').stream()
            buyers = {}
            for doc in docs:
                buyers[doc.id] = doc.to_dict()
            return buyers
        except Exception as e:
            print(f"❌ Error fetching buyers: {e}")
            return {}
        except Exception as e:
            print(f"❌ Error fetching buyers: {e}")
            return {}
    
    def _local_add_umkm(self, umkm_id, umkm_data):
        """Local storage fallback untuk add UMKM"""
        try:
            if not os.path.exists('local_db'):
                os.makedirs('local_db')
            
            umkm_data['created_at'] = datetime.now().isoformat()
            with open(f'local_db/umkm_{umkm_id}.json', 'w') as f:
                json.dump(umkm_data, f, indent=2)
            print(f"✅ UMKM {umkm_id} disimpan lokal")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def _local_get_umkm(self, umkm_id):
        """Local storage fallback untuk get UMKM"""
        try:
            with open(f'local_db/umkm_{umkm_id}.json', 'r') as f:
                return json.load(f)
        except:
            return None
    
    def _local_update_score(self, umkm_id, score, status):
        """Local storage fallback untuk update score"""
        try:
            data = self._local_get_umkm(umkm_id)
            if data:
                data['skor_kesiapan'] = score
                data['status_ekspor'] = status
                data['last_updated'] = datetime.now().isoformat()
                self._local_add_umkm(umkm_id, data)
                return True
            return False
        except:
            return False
    
    def _local_add_transaction(self, transaction_data):
        """Local storage fallback untuk add transaction"""
        try:
            if not os.path.exists('local_db'):
                os.makedirs('local_db')
            
            transaction_data['created_at'] = datetime.now().isoformat()
            import uuid
            trans_id = str(uuid.uuid4())[:8]
            
            with open(f'local_db/transaction_{trans_id}.json', 'w') as f:
                json.dump(transaction_data, f, indent=2)
            return trans_id
        except:
            return None
    
    def _local_get_transactions(self, umkm_id, limit=10):
        """Local storage fallback untuk get transactions"""
        try:
            import glob
            transactions = []
            for file in glob.glob('local_db/transaction_*.json')[:limit]:
                with open(file, 'r') as f:
                    trans = json.load(f)
                    if trans.get('umkm_id') == umkm_id:
                        transactions.append(trans)
            return transactions
        except:
            return []
    
    def _local_add_buyer(self, buyer_id, buyer_data):
        """Local storage fallback untuk add buyer"""
        try:
            if not os.path.exists('local_db'):
                os.makedirs('local_db')
            
            buyer_data['created_at'] = datetime.now().isoformat()
            with open(f'local_db/buyer_{buyer_id}.json', 'w') as f:
                json.dump(buyer_data, f, indent=2)
            return True
        except:
            return False
    
    def _local_get_all_buyers(self):
        """Local storage fallback untuk get all buyers"""
        try:
            import glob
            buyers = {}
            for file in glob.glob('local_db/buyer_*.json'):
                buyer_id = file.split('buyer_')[1].replace('.json', '')
                with open(file, 'r') as f:
                    buyers[buyer_id] = json.load(f)
            return buyers
        except:
            return {}


def get_firebase():
    """Get Firebase Singleton Instance"""
    return FirebaseDB()


def console_log(msg):
    """Print dengan timestamp"""
    from datetime import datetime
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
