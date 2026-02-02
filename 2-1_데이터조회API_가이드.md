# 2-1. 데이터 조회 API 개발 가이드

## 🎯 목표
Google Sheets 데이터를 HTTP GET 요청으로 조회하는 REST API 구축

---

## 📋 구현할 엔드포인트

### 기본 조회
- `GET /api/sites` - 현장 목록
- `GET /api/sites/{id}` - 현장 상세
- `GET /api/personnel` - 인력 목록
- `GET /api/personnel/{id}` - 인력 상세
- `GET /api/certificates` - 자격증 목록
- `GET /api/certificates/{id}` - 자격증 상세

### 부가 기능
- `GET /api/stats` - 통계 정보
- `GET /api/health` - 서버 상태

---

## 🏗️ 1단계: Flask 기본 구조

### 프로젝트 폴더 생성
```bash
mkdir -p api/routes api/services api/models api/utils
touch api/__init__.py
touch api/routes/__init__.py
touch api/services/__init__.py
touch api/models/__init__.py
touch api/utils/__init__.py
```

### api/app.py (메인 앱)
```python
"""
현장배정 관리 시스템 - REST API 서버
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Flask 앱 생성
app = Flask(__name__)

# CORS 설정
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv('ALLOWED_ORIGINS', 'http://localhost:8000').split(','),
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-API-Key"]
    }
})

# 라우트 임포트
from api.routes import sites, personnel, certificates, stats

# 블루프린트 등록
app.register_blueprint(sites.bp, url_prefix='/api')
app.register_blueprint(personnel.bp, url_prefix='/api')
app.register_blueprint(certificates.bp, url_prefix='/api')
app.register_blueprint(stats.bp, url_prefix='/api')

# 루트 엔드포인트
@app.route('/')
def index():
    return jsonify({
        'name': '현장배정 관리 API',
        'version': '1.0.0',
        'endpoints': {
            'sites': '/api/sites',
            'personnel': '/api/personnel',
            'certificates': '/api/certificates',
            'stats': '/api/stats',
            'health': '/api/health'
        }
    })

# 헬스 체크
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'site-management-api',
        'timestamp': datetime.now().isoformat()
    })

# 에러 핸들러
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': {
            'code': 'NOT_FOUND',
            'message': '요청한 리소스를 찾을 수 없습니다'
        }
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': '서버 내부 오류가 발생했습니다'
        }
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    print(f"🚀 서버 시작: http://localhost:{port}")
    print(f"📖 API 문서: http://localhost:{port}/")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
```

---

## 🔧 2단계: Google Sheets 서비스

### api/services/sheets_service.py
```python
"""
Google Sheets 연동 서비스
"""
import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

class SheetsService:
    def __init__(self):
        self.service = self._get_service()
    
    def _get_service(self):
        """Google Sheets API 서비스 생성"""
        creds = None
        
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # client_secret 파일 찾기
                client_secret = None
                for file in os.listdir('.'):
                    if file.startswith('client_secret') and file.endswith('.json'):
                        client_secret = file
                        break
                
                if not client_secret:
                    raise FileNotFoundError("client_secret 파일을 찾을 수 없습니다")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        return build('sheets', 'v4', credentials=creds)
    
    def read_sheet(self, range_name):
        """시트에서 데이터 읽기"""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name
        ).execute()
        
        return result.get('values', [])
    
    def get_all_sites(self):
        """현장 정보 전체 조회"""
        values = self.read_sheet('시트1!A2:W')  # 헤더 제외
        
        if not values:
            return []
        
        sites = []
        for row in values:
            # 컬럼이 부족한 경우 빈 문자열로 채움
            while len(row) < 23:
                row.append('')
            
            site = {
                '현장ID': row[0],
                '현장명': row[1],
                '회사구분': row[2],
                '주소': row[3],
                '위도': row[4],
                '경도': row[5],
                '건축허가일': row[6],
                '착공예정일': row[7],
                '준공일': row[8],
                '현장상태': row[9],
                '특이사항': row[10],
                '담당소장ID': row[11],
                '담당소장명': row[12],  # VLOOKUP 결과
                '담당소장연락처': row[13],  # VLOOKUP 결과
                '사용자격증ID': row[14],
                '자격증명': row[15],  # VLOOKUP 결과
                '자격증소유자명': row[16],  # VLOOKUP 결과
                '자격증소유자연락처': row[17],  # VLOOKUP 결과
                '준공필증파일URL': row[18],
                '배정상태': row[19],
                '등록일': row[20],
                '수정일': row[21]
            }
            sites.append(site)
        
        return sites
    
    def get_site_by_id(self, site_id):
        """현장ID로 현장 정보 조회"""
        sites = self.get_all_sites()
        
        for site in sites:
            if site['현장ID'] == site_id:
                return site
        
        return None
    
    def get_all_personnel(self):
        """인력 정보 전체 조회"""
        values = self.read_sheet('시트2!A2:L')
        
        if not values:
            return []
        
        personnel_list = []
        for row in values:
            while len(row) < 12:
                row.append('')
            
            person = {
                '인력ID': row[0],
                '성명': row[1],
                '직책': row[2],
                '소속': row[3],
                '연락처': row[4],
                '이메일': row[5],
                '보유자격증': row[6],
                '현재상태': row[7],
                '현재담당현장수': row[8],
                '비고': row[9],
                '입사일': row[10],
                '등록일': row[11]
            }
            personnel_list.append(person)
        
        return personnel_list
    
    def get_personnel_by_id(self, personnel_id):
        """인력ID로 인력 정보 조회"""
        personnel = self.get_all_personnel()
        
        for person in personnel:
            if person['인력ID'] == personnel_id:
                return person
        
        return None
    
    def get_all_certificates(self):
        """자격증 정보 전체 조회"""
        values = self.read_sheet('시트3!A2:M')
        
        if not values:
            return []
        
        certificates = []
        for row in values:
            while len(row) < 13:
                row.append('')
            
            cert = {
                '자격증ID': row[0],
                '자격증명': row[1],
                '자격증번호': row[2],
                '소유자ID': row[3],
                '소유자명': row[4],
                '소유자연락처': row[5],
                '발급기관': row[6],
                '취득일': row[7],
                '유효기간': row[8],
                '사용가능여부': row[9],
                '현재사용현장ID': row[10],
                '비고': row[11],
                '등록일': row[12]
            }
            certificates.append(cert)
        
        return certificates
    
    def get_certificate_by_id(self, cert_id):
        """자격증ID로 자격증 정보 조회"""
        certificates = self.get_all_certificates()
        
        for cert in certificates:
            if cert['자격증ID'] == cert_id:
                return cert
        
        return None

# 싱글톤 인스턴스
sheets_service = SheetsService()
```

---

## 🛣️ 3단계: 라우트 구현

### api/routes/sites.py (현장 라우트)
```python
"""
현장 관련 API 라우트
"""
from flask import Blueprint, jsonify, request
from api.services.sheets_service import sheets_service
from datetime import datetime

bp = Blueprint('sites', __name__)

@bp.route('/sites', methods=['GET'])
def get_sites():
    """현장 목록 조회 (필터링 지원)"""
    try:
        # 전체 현장 조회
        sites = sheets_service.get_all_sites()
        
        # 쿼리 파라미터로 필터링
        company = request.args.get('company')  # 회사구분
        status = request.args.get('status')    # 배정상태
        state = request.args.get('state')      # 현장상태
        
        # 필터 적용
        if company:
            sites = [s for s in sites if s['회사구분'] == company]
        
        if status:
            sites = [s for s in sites if s['배정상태'] == status]
        
        if state:
            sites = [s for s in sites if s['현장상태'] == state]
        
        return jsonify({
            'success': True,
            'data': sites,
            'count': len(sites),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': str(e)
            }
        }), 500

@bp.route('/sites/<site_id>', methods=['GET'])
def get_site_detail(site_id):
    """현장 상세 조회 (관계 데이터 포함)"""
    try:
        # 현장 정보
        site = sheets_service.get_site_by_id(site_id)
        
        if not site:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SITE_NOT_FOUND',
                    'message': f'현장ID {site_id}를 찾을 수 없습니다'
                }
            }), 404
        
        # 담당소장 정보 (이미 VLOOKUP으로 포함됨)
        if site['담당소장ID']:
            site['manager'] = {
                'id': site['담당소장ID'],
                'name': site['담당소장명'],
                'phone': site['담당소장연락처']
            }
        
        # 사용자격증 정보 (이미 VLOOKUP으로 포함됨)
        if site['사용자격증ID']:
            site['certificate'] = {
                'id': site['사용자격증ID'],
                'name': site['자격증명'],
                'owner': site['자격증소유자명'],
                'phone': site['자격증소유자연락처']
            }
        
        return jsonify({
            'success': True,
            'data': site,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': str(e)
            }
        }), 500

@bp.route('/sites/search', methods=['GET'])
def search_sites():
    """현장 검색 (현장명, 주소로 검색)"""
    try:
        query = request.args.get('q', '').lower()
        
        if not query:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_QUERY',
                    'message': '검색어를 입력해주세요'
                }
            }), 400
        
        sites = sheets_service.get_all_sites()
        
        # 현장명 또는 주소에 검색어 포함
        results = [
            s for s in sites 
            if query in s['현장명'].lower() or query in s['주소'].lower()
        ]
        
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results),
            'query': query,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SEARCH_ERROR',
                'message': str(e)
            }
        }), 500
```

### api/routes/personnel.py (인력 라우트)
```python
"""
인력 관련 API 라우트
"""
from flask import Blueprint, jsonify, request
from api.services.sheets_service import sheets_service
from datetime import datetime

bp = Blueprint('personnel', __name__)

@bp.route('/personnel', methods=['GET'])
def get_personnel():
    """인력 목록 조회 (필터링 지원)"""
    try:
        personnel = sheets_service.get_all_personnel()
        
        # 필터링
        status = request.args.get('status')    # 현재상태
        role = request.args.get('role')        # 직책
        
        if status:
            personnel = [p for p in personnel if p['현재상태'] == status]
        
        if role:
            personnel = [p for p in personnel if p['직책'] == role]
        
        return jsonify({
            'success': True,
            'data': personnel,
            'count': len(personnel),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': str(e)
            }
        }), 500

@bp.route('/personnel/<personnel_id>', methods=['GET'])
def get_personnel_detail(personnel_id):
    """인력 상세 조회"""
    try:
        person = sheets_service.get_personnel_by_id(personnel_id)
        
        if not person:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PERSONNEL_NOT_FOUND',
                    'message': f'인력ID {personnel_id}를 찾을 수 없습니다'
                }
            }), 404
        
        return jsonify({
            'success': True,
            'data': person,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': str(e)
            }
        }), 500
```

### api/routes/certificates.py (자격증 라우트)
```python
"""
자격증 관련 API 라우트
"""
from flask import Blueprint, jsonify, request
from api.services.sheets_service import sheets_service
from datetime import datetime

bp = Blueprint('certificates', __name__)

@bp.route('/certificates', methods=['GET'])
def get_certificates():
    """자격증 목록 조회 (필터링 지원)"""
    try:
        certificates = sheets_service.get_all_certificates()
        
        # 필터링
        available = request.args.get('available')  # 사용가능 여부
        
        if available == 'true':
            certificates = [c for c in certificates if c['사용가능여부'] == '사용가능']
        elif available == 'false':
            certificates = [c for c in certificates if c['사용가능여부'] != '사용가능']
        
        return jsonify({
            'success': True,
            'data': certificates,
            'count': len(certificates),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': str(e)
            }
        }), 500

@bp.route('/certificates/<cert_id>', methods=['GET'])
def get_certificate_detail(cert_id):
    """자격증 상세 조회"""
    try:
        cert = sheets_service.get_certificate_by_id(cert_id)
        
        if not cert:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CERTIFICATE_NOT_FOUND',
                    'message': f'자격증ID {cert_id}를 찾을 수 없습니다'
                }
            }), 404
        
        return jsonify({
            'success': True,
            'data': cert,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': str(e)
            }
        }), 500
```

### api/routes/stats.py (통계 라우트)
```python
"""
통계 관련 API 라우트
"""
from flask import Blueprint, jsonify
from api.services.sheets_service import sheets_service
from datetime import datetime

bp = Blueprint('stats', __name__)

@bp.route('/stats', methods=['GET'])
def get_statistics():
    """전체 통계 정보"""
    try:
        sites = sheets_service.get_all_sites()
        personnel = sheets_service.get_all_personnel()
        certificates = sheets_service.get_all_certificates()
        
        # 현장 통계
        site_stats = {
            'total': len(sites),
            'assigned': len([s for s in sites if s['배정상태'] == '배정완료']),
            'unassigned': len([s for s in sites if s['배정상태'] == '미배정']),
            'by_company': {
                '더존종합건설': len([s for s in sites if s['회사구분'] == '더존종합건설']),
                '더존하우징': len([s for s in sites if s['회사구분'] == '더존하우징'])
            },
            'by_state': {}
        }
        
        # 현장상태별 집계
        for site in sites:
            state = site['현장상태']
            site_stats['by_state'][state] = site_stats['by_state'].get(state, 0) + 1
        
        # 인력 통계
        personnel_stats = {
            'total': len(personnel),
            'available': len([p for p in personnel if p['현재상태'] == '투입가능']),
            'deployed': len([p for p in personnel if p['현재상태'] == '투입중']),
            'by_role': {}
        }
        
        for person in personnel:
            role = person['직책']
            personnel_stats['by_role'][role] = personnel_stats['by_role'].get(role, 0) + 1
        
        # 자격증 통계
        cert_stats = {
            'total': len(certificates),
            'available': len([c for c in certificates if c['사용가능여부'] == '사용가능']),
            'in_use': len([c for c in certificates if c['사용가능여부'] == '사용중']),
            'expired': len([c for c in certificates if c['사용가능여부'] == '만료'])
        }
        
        return jsonify({
            'success': True,
            'data': {
                'sites': site_stats,
                'personnel': personnel_stats,
                'certificates': cert_stats
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'STATS_ERROR',
                'message': str(e)
            }
        }), 500
```

---

## 🧪 테스트

### 서버 실행
```bash
cd 현장배정현황
python api/app.py
```

### curl 테스트
```bash
# 헬스 체크
curl http://localhost:5000/api/health

# 현장 전체 조회
curl http://localhost:5000/api/sites

# 현장 필터링 (미배정만)
curl "http://localhost:5000/api/sites?status=미배정"

# 현장 상세 조회
curl http://localhost:5000/api/sites/S001

# 현장 검색
curl "http://localhost:5000/api/sites/search?q=평택"

# 인력 조회 (투입가능만)
curl "http://localhost:5000/api/personnel?status=투입가능"

# 자격증 조회 (사용가능만)
curl "http://localhost:5000/api/certificates?available=true"

# 통계
curl http://localhost:5000/api/stats
```

---

## ✅ 체크리스트

- [ ] Flask 서버 정상 실행
- [ ] 헬스 체크 정상 응답
- [ ] 현장 목록 조회 성공
- [ ] 현장 필터링 정상 작동
- [ ] 현장 상세 조회 성공
- [ ] 인력 목록 조회 성공
- [ ] 자격증 목록 조회 성공
- [ ] 통계 API 정상 작동
- [ ] 에러 핸들링 정상 작동

---

**완료 시간**: 약 4시간  
**난이도**: ⭐⭐⭐☆☆  
**다음 단계**: 데이터 수정 API 개발
