# utils/ai_engine.py
import pandas as pd
import numpy as np
import joblib
import os

# ============================================================================
# IMPROVED INFERENCE ENGINE - ANTI-BIAS VERSION
# ============================================================================
# Perbaikan:
# 1. Use StandardScaler from training (proper feature scaling)
# 2. Confidence score dari ensemble variance
# 3. Feature validation & sanitization
# 4. Better uncertainty quantification
# 5. Improved fallback with domain knowledge
# ============================================================================

def predict_readiness_score(umkm_data):
    """
    Memprediksi skor kesiapan ekspor dengan confidence score
    
    Returns:
        dict: {
            'score': int (0-100),
            'confidence': float (0-1),
            'model_used': str,
            'uncertainty': float,
            'details': dict
        }
    """
    try:
        model_path = 'models/model_scoring.pkl'
        
        # Fallback jika model belum di-train
        if not os.path.exists(model_path):
            print("⚠️ Model ML tidak ditemukan, menggunakan rule-based fallback.")
            return _get_fallback_result(_rule_based_scoring(umkm_data), confidence=0.4)
        
        # 1. LOAD MODEL ARTIFACT
        model_payload = joblib.load(model_path)

        if isinstance(model_payload, dict) and 'estimator' in model_payload:
            model = model_payload['estimator']
            scaler = model_payload.get('scaler')  # ✓ NEW: Get scaler
            y_min = model_payload.get('y_min', 0)
            y_max = model_payload.get('y_max', 100)
            features = model_payload.get('features')  # ✓ NEW: Expected features
            metrics = model_payload.get('metrics', {})  # ✓ NEW: Model metrics
        else:
            # Backward compatibility
            model = model_payload
            scaler = None
            y_min, y_max = 0, 100
            features = None
            metrics = {}

        # 2. FEATURE VALIDATION & FORMATTING
        if features is None:
            # Fallback feature list
            features = [
                'tahun_berdiri', 'modal_usaha', 'omzet_bulanan', 'jumlah_karyawan',
                'punya_sertifikat_halal', 'punya_sertifikat_bpom', 'punya_nib',
                'ekspor_sebelumnya', 'kapasitas_produksi'
            ]
        
        # ✓ NEW: Validate & sanitize input
        validated_data = _validate_input(umkm_data, features)
        input_df = pd.DataFrame([validated_data])[features]

        # 3. SCALING (if scaler available)
        if scaler is not None:
            input_scaled = scaler.transform(input_df)
        else:
            input_scaled = input_df.values

        # 4. GET INDIVIDUAL PREDICTIONS from ensemble estimators
        # For confidence score, we need predictions from both RF and GB
        predictions_individual = []
        for name, estimator in model.estimators:
            try:
                if scaler is not None:
                    pred = estimator.predict(input_scaled)[0]
                else:
                    pred = estimator.predict(input_df)[0]
                predictions_individual.append(pred)
            except:
                pass
        
        # 5. ENSEMBLE PREDICTION
        if scaler is not None:
            raw_score = model.predict(input_scaled)[0]
        else:
            raw_score = model.predict(input_df)[0]

        # 6. CALIBRATION to 0-100 scale
        if y_max > y_min:
            calibrated_score = (raw_score - y_min) / (y_max - y_min) * 100
        else:
            calibrated_score = raw_score

        calibrated_score = float(np.clip(calibrated_score, 0, 100))
        score = int(calibrated_score)

        # 7. CONFIDENCE SCORE from ensemble variance
        if len(predictions_individual) > 1:
            # Variance between RF and GB predictions
            variance = np.var(predictions_individual)
            # Normalize variance to confidence (lower variance = higher confidence)
            max_variance = y_max - y_min
            confidence = max(0.5, 1 - (variance / max_variance))  # Min 0.5 confidence
        else:
            confidence = 0.7  # Default moderate confidence
        
        # Adjust confidence based on model test performance
        test_r2 = metrics.get('r2_test', 0.5)
        confidence = confidence * (0.5 + test_r2 / 2)  # Scale by model accuracy

        # 8. UNCERTAINTY ESTIMATION
        uncertainty = 1 - confidence
        uncertainty_range = uncertainty * 10  # Roughly ±10 in score space per uncertainty point

        result = {
            'score': score,
            'confidence': float(np.clip(confidence, 0, 1)),
            'model_used': 'ensemble_ml',
            'uncertainty': float(uncertainty),
            'uncertainty_range': round(uncertainty_range, 1),
            'details': {
                'raw_predictions': [round(p, 2) for p in predictions_individual],
                'calibrated_value': round(calibrated_score, 2),
                'model_quality_r2': metrics.get('r2_test', 0.5)
            }
        }
        
        return result
    
    except Exception as e:
        print(f"❌ Error pada sistem AI: {e}")
        return _get_fallback_result(_rule_based_scoring(umkm_data), confidence=0.3, error=str(e))


def _validate_input(umkm_data, features):
    """Validate dan sanitize input data"""
    validated = {}
    
    for feature in features:
        if feature not in umkm_data:
            # ✓ NEW: Provide default for missing features
            validated[feature] = _get_feature_default(feature)
            print(f"⚠️ Missing feature '{feature}', using default value")
        else:
            value = umkm_data[feature]
            # Sanitize numeric values
            if isinstance(value, str):
                try:
                    value = float(value)
                except:
                    value = _get_feature_default(feature)
            
            # Clip to reasonable ranges
            if feature == 'tahun_berdiri':
                value = int(np.clip(value, 1900, 2026))
            elif feature in ['modal_usaha', 'omzet_bulanan']:
                value = float(np.clip(value, 0, 1e9))
            elif feature == 'jumlah_karyawan':
                value = int(np.clip(value, 1, 10000))
            elif feature == 'kapasitas_produksi':
                value = int(np.clip(value, 1, 50000))
            elif feature in ['punya_nib', 'punya_sertifikat_halal', 'punya_sertifikat_bpom', 'ekspor_sebelumnya']:
                value = int(bool(value))
            
            validated[feature] = value
    
    return validated


def _get_feature_default(feature):
    """Get default value for missing feature"""
    defaults = {
        'tahun_berdiri': 2020,
        'modal_usaha': 50000000,
        'omzet_bulanan': 10000000,
        'jumlah_karyawan': 5,
        'punya_sertifikat_halal': 0,
        'punya_sertifikat_bpom': 0,
        'punya_nib': 0,
        'ekspor_sebelumnya': 0,
        'kapasitas_produksi': 100
    }
    return defaults.get(feature, 0)


def _rule_based_scoring(umkm_data):
    """Sistem cadangan (fallback) jika Machine Learning gagal"""
    score = 30  # Base score (same as training)
    
    # Sertifikasi
    if umkm_data.get('punya_nib'): score += 10
    if umkm_data.get('punya_sertifikat_halal'): score += 8
    if umkm_data.get('punya_sertifikat_bpom'): score += 12
    if umkm_data.get('ekspor_sebelumnya'): score += 15
    
    # Scale indicators
    omzet = umkm_data.get('omzet_bulanan', 0)
    modal = umkm_data.get('modal_usaha', 0)
    kapasitas = umkm_data.get('kapasitas_produksi', 0)
    
    if omzet > 50000000: score += 10
    if omzet > 100000000: score += 5
    if modal > 100000000: score += 8
    if kapasitas > 1000: score += 10
    
    # Experience
    years_operating = 2026 - umkm_data.get('tahun_berdiri', 2026)
    if years_operating >= 5: score += 5
    if years_operating >= 10: score += 3
    
    return int(min(100, score))


def _get_fallback_result(score, confidence=0.0, error=None):
    """Format fallback result"""
    result = {
        'score': score,
        'confidence': confidence,
        'model_used': 'rule_based_fallback',
        'uncertainty': 1 - confidence,
        'uncertainty_range': round((1 - confidence) * 15, 1),  # Higher uncertainty for fallback
        'details': {
            'raw_predictions': [score],
            'calibrated_value': float(score),
            'model_quality_r2': 0.0
        }
    }
    
    if error:
        result['error_message'] = error
    
    return result