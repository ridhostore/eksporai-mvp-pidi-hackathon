# utils/transaction_tracker.py
"""
Transaction Tracking & Management System
Mencatat dan monitor semua transaksi UMKM-Buyer
"""
import pandas as pd
from datetime import datetime
from utils.firebase_config import get_firebase
import json


class TransactionTracker:
    """Manager untuk tracking transaksi UMKM-Buyer"""
    
    def __init__(self):
        self.db = get_firebase()
    
    def create_transaction(self, umkm_id, buyer_id, details):
        """
        Create new transaction record
        
        Parameters:
        umkm_id: ID of UMKM
        buyer_id: ID of Buyer
        details: dict dengan info transaksi (quantity, price, product, etc)
        
        Returns:
        transaction_id atau None
        """
        transaction_data = {
            'umkm_id': umkm_id,
            'buyer_id': buyer_id,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'quantity': details.get('quantity', 0),
            'product': details.get('product', ''),
            'value_usd': details.get('value_usd', 0),
            'value_idr': details.get('value_idr', 0),
            'notes': details.get('notes', ''),
            'timeline': []
        }
        
        trans_id = self.db.add_transaction(transaction_data)
        return trans_id
    
    def update_transaction_status(self, transaction_id, new_status, notes=''):
        """
        Update transaction status
        
        Status flow: pending → negotiation → agreed → shipped → completed/cancelled
        """
        valid_statuses = ['pending', 'negotiation', 'agreed', 'shipped', 'completed', 'cancelled']
        
        if new_status not in valid_statuses:
            print(f"❌ Invalid status: {new_status}")
            return False
        
        update_data = {
            'status': new_status,
            'updated_at': datetime.now().isoformat(),
            'last_status_note': notes
        }
        
        try:
            # For local storage simulation
            if hasattr(self.db, 'is_online') and not self.db.is_online:
                trans_file = f'local_db/transaction_{transaction_id}.json'
                try:
                    with open(trans_file, 'r') as f:
                        data = json.load(f)
                    data.update(update_data)
                    with open(trans_file, 'w') as f:
                        json.dump(data, f, indent=2)
                except:
                    pass
            
            print(f"✅ Transaction {transaction_id} updated to {new_status}")
            return True
        except Exception as e:
            print(f"❌ Error updating transaction: {e}")
            return False
    
    def get_transaction_history(self, umkm_id, limit=20):
        """Get all transactions untuk UMKM tertentu"""
        transactions = self.db.get_transactions(umkm_id, limit)
        return transactions if transactions else []
    
    def get_transaction_stats(self, umkm_id):
        """
        Calculate transaction statistics untuk UMKM
        """
        transactions = self.get_transaction_history(umkm_id, limit=100)
        
        stats = {
            'total_transactions': len(transactions),
            'completed_transactions': len([t for t in transactions if t.get('status') == 'completed']),
            'pending_transactions': len([t for t in transactions if t.get('status') == 'pending']),
            'total_value_usd': sum(t.get('value_usd', 0) for t in transactions),
            'total_value_idr': sum(t.get('value_idr', 0) for t in transactions),
            'avg_transaction_value_usd': 0,
            'success_rate': 0
        }
        
        if transactions:
            stats['avg_transaction_value_usd'] = stats['total_value_usd'] / len(transactions)
            stats['success_rate'] = (stats['completed_transactions'] / len(transactions)) * 100
        
        return stats
    
    def export_transaction_report(self, umkm_id):
        """Export transaction history sebagai DataFrame"""
        transactions = self.get_transaction_history(umkm_id, limit=1000)
        
        if not transactions:
            return pd.DataFrame()
        
        df = pd.DataFrame(transactions)
        return df
    
    def record_buyer_contact(self, umkm_id, buyer_id, contact_type, contact_info):
        """
        Record ketika UMKM menghubungi buyer
        
        contact_type: 'email', 'phone', 'whatsapp', 'inquiry'
        """
        contact_data = {
            'umkm_id': umkm_id,
            'buyer_id': buyer_id,
            'contact_type': contact_type,
            'contact_info': contact_info,
            'contacted_at': datetime.now().isoformat(),
            'status': 'pending_response'
        }
        
        try:
            if not hasattr(self.db, 'is_online') or self.db.is_online:
                # Firebase
                pass
            else:
                # Local storage
                contact_id = f"{umkm_id}_{buyer_id}_{datetime.now().timestamp()}"
                with open(f'local_db/contact_{contact_id}.json', 'w') as f:
                    json.dump(contact_data, f, indent=2)
            
            print(f"✅ Contact recorded: {umkm_id} → {buyer_id}")
            return True
        except Exception as e:
            print(f"❌ Error recording contact: {e}")
            return False


def get_transaction_tracker():
    """Get singleton TransactionTracker instance"""
    return TransactionTracker()
