// 현장 데이터 (샘플 225개)
const sitesData = [
    // 더존종합건설 - 경기도 (50개)
    { 
        id: 'S001', name: '평택 푸르지오', company: '종합', address: '경기도 평택시 비전동 123', 
        lat: 36.9921, lng: 126.9730, 
        permitDate: '2025-12-10', startDate: '2026-03-15', completionDate: '2027-12-30',
        siteStatus: '착공예정', specialNotes: '대단지 아파트 (1,200세대)',
        manager: '김현장', managerPhone: '010-1234-5678',
        certName: '건축기사', certOwner: '김현장', certPhone: '010-1234-5678',
        completionCertFile: null,
        status: '배정완료' 
    },
    { 
        id: 'S002', name: '수원 힐스테이트', company: '종합', address: '경기도 수원시 영통구 원천동 456', 
        lat: 37.2636, lng: 127.0286, 
        permitDate: '2026-01-05', startDate: '2026-04-01', completionDate: '2027-10-15',
        siteStatus: '착공예정', specialNotes: '역세권 개발',
        manager: '이소장', managerPhone: '010-2345-6789',
        certName: '건축산업기사', certOwner: '이소장', certPhone: '010-2345-6789',
        completionCertFile: null,
        status: '배정완료' 
    },
    { 
        id: 'S003', name: '용인 동백 자이', company: '종합', address: '경기도 용인시 기흥구 동백동 789', 
        lat: 37.2639, lng: 127.1483, 
        permitDate: '2026-02-20', startDate: '2026-05-10', completionDate: '2028-03-20',
        siteStatus: '건축허가', specialNotes: '학군지 인기단지',
        manager: '', managerPhone: '',
        certName: '건축기사', certOwner: '박사무실장', certPhone: '010-9999-1111',
        completionCertFile: null,
        status: '미배정' 
    },
    { 
        id: 'S004', name: '화성 동탄2 레이크포레', company: '종합', address: '경기도 화성시 동탄면 234', 
        lat: 37.2000, lng: 127.0750, 
        permitDate: '2025-11-30', startDate: '2026-03-25', completionDate: '2027-11-10',
        siteStatus: '착공예정', specialNotes: '호수공원 조망',
        manager: '박건설', managerPhone: '010-3456-7890',
        certName: '건축기사, 안전관리자', certOwner: '박건설', certPhone: '010-3456-7890',
        completionCertFile: null,
        status: '배정완료' 
    },
    { 
        id: 'S005', name: '성남 판교 센트럴', company: '종합', address: '경기도 성남시 분당구 판교동 567', 
        lat: 37.3944, lng: 127.1110, 
        permitDate: '2026-03-15', startDate: '2026-06-01', completionDate: '2028-05-30',
        siteStatus: '건축허가', specialNotes: 'IT밸리 인접',
        manager: '', managerPhone: '',
        certName: '건축기사', certOwner: '최사무실', certPhone: '010-8888-2222',
        completionCertFile: null,
        status: '미배정' 
    },
    { 
        id: 'S006', name: '안양 평촌 롯데캐슬', company: '종합', address: '경기도 안양시 동안구 평촌동 890', 
        lat: 37.3894, lng: 126.9511, 
        permitDate: '2026-01-10', startDate: '2026-04-15', completionDate: '2027-12-20',
        siteStatus: '착공예정', specialNotes: '재개발 사업',
        manager: '최관리', managerPhone: '010-4567-8901',
        certName: '건축기사, 안전관리자', certOwner: '최관리', certPhone: '010-4567-8901',
        completionCertFile: null,
        status: '배정완료' 
    },
    { 
        id: 'S007', name: '부천 상동 힐스테이트', company: '종합', address: '경기도 부천시 원미구 상동 123', 
        lat: 37.4989, lng: 126.7658, 
        permitDate: '2026-02-05', startDate: '2026-05-20', completionDate: '2028-01-15',
        siteStatus: '착공예정', specialNotes: '도심형 생활주택',
        manager: '정현장', managerPhone: '010-5678-9012',
        certName: '건축산업기사', certOwner: '정현장', certPhone: '010-5678-9012',
        completionCertFile: null,
        status: '배정완료' 
    },
    { 
        id: 'S008', name: '광명 하안 자이', company: '종합', address: '경기도 광명시 하안동 456', 
        lat: 37.4778, lng: 126.8650, 
        permitDate: '2025-12-28', startDate: '2026-03-30', completionDate: '2027-09-25',
        siteStatus: '착공예정', specialNotes: '서울 접근성 우수',
        manager: '', managerPhone: '',
        certName: '건축기사', certOwner: '강사무직원', certPhone: '010-7777-3333',
        completionCertFile: null,
        status: '미배정' 
    },
    { 
        id: 'S009', name: '시흥 능곡 푸르지오', company: '종합', address: '경기도 시흥시 능곡동 789', 
        lat: 37.3806, lng: 126.8031, 
        permitDate: '2026-04-01', startDate: '2026-07-01', completionDate: '2028-06-15',
        siteStatus: '건축허가', specialNotes: '신도시 개발지역',
        manager: '강소장', managerPhone: '010-6789-0123',
        certName: '건축기사', certOwner: '강소장', certPhone: '010-6789-0123',
        completionCertFile: null,
        status: '배정완료' 
    },
    { 
        id: 'S010', name: '안산 고잔 e편한세상', company: '종합', address: '경기도 안산시 단원구 고잔동 234', 
        lat: 37.3189, lng: 126.8300, 
        permitDate: '2026-01-20', startDate: '2026-04-20', completionDate: '2027-11-30',
        siteStatus: '착공예정', specialNotes: '교통 편리',
        manager: '윤현장', managerPhone: '010-7890-1234',
        certName: '건축산업기사', certOwner: '윤현장', certPhone: '010-7890-1234',
        completionCertFile: null,
        status: '배정완료' 
    },
    
    // 더존하우징 - 경기도 (50개)
    { 
        id: 'H001', name: '평택 비전 더샵', company: '하우징', address: '경기도 평택시 비전동 345', 
        lat: 36.9950, lng: 126.9800, 
        permitDate: '2025-12-01', startDate: '2026-03-10', completionDate: '2027-11-15',
        siteStatus: '착공예정', specialNotes: '주상복합',
        manager: '임건축', managerPhone: '010-8901-2345',
        certName: '건축기사', certOwner: '임건축', certPhone: '010-8901-2345',
        completionCertFile: null,
        status: '배정완료' 
    },
    { 
        id: 'H002', name: '오산 세교 힐스테이트', company: '하우징', address: '경기도 오산시 세교동 678', 
        lat: 37.1500, lng: 127.0700, 
        permitDate: '2026-01-15', startDate: '2026-04-05', completionDate: '2027-12-10',
        siteStatus: '착공예정', specialNotes: '신규 택지지구',
        manager: '', managerPhone: '',
        certName: '건축기사', certOwner: '김사무직원', certPhone: '010-6666-4444',
        completionCertFile: null,
        status: '미배정' 
    },
    { 
        id: 'H003', name: '용인 수지 자이', company: '하우징', address: '경기도 용인시 수지구 901', 
        lat: 37.3256, lng: 127.0989, 
        permitDate: '2026-02-10', startDate: '2026-05-15', completionDate: '2028-02-28',
        siteStatus: '건축허가', specialNotes: '명문학군',
        manager: '한소장', managerPhone: '010-9012-3456',
        certName: '건축산업기사', certOwner: '한소장', certPhone: '010-9012-3456',
        completionCertFile: null,
        status: '배정완료' 
    },
    { 
        id: 'H004', name: '화성 봉담 롯데캐슬', company: '하우징', address: '경기도 화성시 봉담읍 234', 
        lat: 37.2194, lng: 126.9322, 
        permitDate: '2025-11-20', startDate: '2026-03-20', completionDate: '2027-10-05',
        siteStatus: '착공예정', specialNotes: '브랜드 인지도',
        manager: '송현장', managerPhone: '010-0123-4567',
        certName: '건축기사', certOwner: '송현장', certPhone: '010-0123-4567',
        completionCertFile: null,
        status: '배정완료' 
    },
    { 
        id: 'H005', name: '고양 일산 e편한세상', company: '하우징', address: '경기도 고양시 일산서구 567', 
        lat: 37.6564, lng: 126.7689, 
        permitDate: '2026-03-20', startDate: '2026-06-10', completionDate: '2028-04-20',
        siteStatus: '건축허가', specialNotes: '신도시 중심',
        manager: '', managerPhone: '',
        certName: '건축기사', certOwner: '이사무실', certPhone: '010-5555-5555',
        completionCertFile: null,
        status: '미배정' 
    },
    { id: 'H006', name: '파주 운정 푸르지오', company: '하우징', address: '경기도 파주시 운정동 890', lat: 37.7600, lng: 126.7450, startDate: '2026-04-25', manager: '구관리', phone: '010-1234-5679', cert: '건축기사, 안전관리자', status: '배정완료' },
    { id: 'H007', name: '김포 장기 힐스테이트', company: '하우징', address: '경기도 김포시 장기동 123', lat: 37.6350, lng: 126.7150, startDate: '2026-05-30', manager: '배소장', phone: '010-2345-6780', cert: '건축산업기사', status: '배정완료' },
    { id: 'H008', name: '남양주 다산 자이', company: '하우징', address: '경기도 남양주시 다산동 456', lat: 37.6361, lng: 127.1547, startDate: '2026-03-18', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'H009', name: '하남 미사 푸르지오', company: '하우징', address: '경기도 하남시 미사동 789', lat: 37.5556, lng: 127.1833, startDate: '2026-07-05', manager: '서현장', phone: '010-3456-7891', cert: '건축기사', status: '배정완료' },
    { id: 'H010', name: '양주 옥정 e편한세상', company: '하우징', address: '경기도 양주시 옥정동 234', lat: 37.8194, lng: 127.0467, startDate: '2026-04-18', manager: '권소장', phone: '010-4567-8902', cert: '건축산업기사', status: '배정완료' },
    
    // 더존종합건설 - 충청도 (30개)
    { id: 'S011', name: '천안 두정 롯데캐슬', company: '종합', address: '충남 천안시 서북구 두정동 567', lat: 36.8353, lng: 127.1389, startDate: '2026-03-12', manager: '민건축', phone: '010-5678-9013', cert: '건축기사', status: '배정완료' },
    { id: 'S012', name: '아산 탕정 힐스테이트', company: '종합', address: '충남 아산시 탕정면 890', lat: 36.7806, lng: 127.1117, startDate: '2026-04-08', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'S013', name: '청주 율량 자이', company: '종합', address: '충북 청주시 청원구 율량동 123', lat: 36.6572, lng: 127.4886, startDate: '2026-05-22', manager: '문소장', phone: '010-6789-0124', cert: '건축산업기사', status: '배정완료' },
    { id: 'S014', name: '세종 조치원 푸르지오', company: '종합', address: '세종시 조치원읍 456', lat: 36.5994, lng: 127.2906, startDate: '2026-03-28', manager: '진현장', phone: '010-7890-1235', cert: '건축기사', status: '배정완료' },
    { id: 'S015', name: '공주 신관 e편한세상', company: '종합', address: '충남 공주시 신관동 789', lat: 36.4595, lng: 127.1189, startDate: '2026-06-15', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'S016', name: '천안 신방 롯데캐슬', company: '종합', address: '충남 천안시 동남구 신방동 234', lat: 36.7994, lng: 127.1536, startDate: '2026-04-22', manager: '류관리', phone: '010-8901-2346', cert: '건축기사, 안전관리자', status: '배정완료' },
    { id: 'S017', name: '당진 합덕 힐스테이트', company: '종합', address: '충남 당진시 합덕읍 567', lat: 36.8978, lng: 126.6356, startDate: '2026-05-28', manager: '조소장', phone: '010-9012-3457', cert: '건축산업기사', status: '배정완료' },
    { id: 'S018', name: '청주 복대 자이', company: '종합', address: '충북 청주시 서원구 복대동 890', lat: 36.6236, lng: 127.4611, startDate: '2026-03-16', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'S019', name: '충주 연수 푸르지오', company: '종합', address: '충북 충주시 연수동 123', lat: 36.9911, lng: 127.9264, startDate: '2026-07-08', manager: '오현장', phone: '010-0123-4568', cert: '건축기사', status: '배정완료' },
    { id: 'S020', name: '보령 대천 e편한세상', company: '종합', address: '충남 보령시 대천동 456', lat: 36.3333, lng: 126.6128, startDate: '2026-04-12', manager: '양소장', phone: '010-1234-5680', cert: '건축산업기사', status: '배정완료' },
    
    // 더존하우징 - 충청도 (30개)
    { id: 'H011', name: '천안 백석 더샵', company: '하우징', address: '충남 천안시 서북구 백석동 789', lat: 36.8194, lng: 127.1547, startDate: '2026-03-14', manager: '홍건축', phone: '010-2345-6781', cert: '건축기사', status: '배정완료' },
    { id: 'H012', name: '아산 배방 힐스테이트', company: '하우징', address: '충남 아산시 배방읍 234', lat: 36.7722, lng: 127.0511, startDate: '2026-04-19', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'H013', name: '청주 강서 자이', company: '하우징', address: '충북 청주시 흥덕구 강서동 567', lat: 36.6347, lng: 127.4117, startDate: '2026-05-25', manager: '표소장', phone: '010-3456-7892', cert: '건축산업기사', status: '배정완료' },
    { id: 'H014', name: '세종 나성 롯데캐슬', company: '하우징', address: '세종시 나성동 890', lat: 36.5078, lng: 127.2647, startDate: '2026-03-22', manager: '노현장', phone: '010-4567-8903', cert: '건축기사', status: '배정완료' },
    { id: 'H015', name: '논산 취암 푸르지오', company: '하우징', address: '충남 논산시 취암동 123', lat: 36.1869, lng: 127.0989, startDate: '2026-06-20', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'H016', name: '천안 쌍용 e편한세상', company: '하우징', address: '충남 천안시 서북구 쌍용동 456', lat: 36.8028, lng: 127.1194, startDate: '2026-04-28', manager: '주관리', phone: '010-5678-9014', cert: '건축기사, 안전관리자', status: '배정완료' },
    { id: 'H017', name: '서산 읍내 힐스테이트', company: '하우징', address: '충남 서산시 읍내동 789', lat: 36.7847, lng: 126.4503, startDate: '2026-06-02', manager: '차소장', phone: '010-6789-0125', cert: '건축산업기사', status: '배정완료' },
    { id: 'H018', name: '청주 사창 자이', company: '하우징', address: '충북 청주시 흥덕구 사창동 234', lat: 36.6428, lng: 127.4378, startDate: '2026-03-24', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'H019', name: '제천 청전 푸르지오', company: '하우징', address: '충북 제천시 청전동 567', lat: 37.1325, lng: 128.1908, startDate: '2026-07-12', manager: '신현장', phone: '010-7890-1236', cert: '건축기사', status: '배정완료' },
    { id: 'H020', name: '태안 안면 e편한세상', company: '하우징', address: '충남 태안군 안면읍 890', lat: 36.5319, lng: 126.3200, startDate: '2026-04-16', manager: '유소장', phone: '010-8901-2347', cert: '건축산업기사', status: '배정완료' },
    
    // 경상도 및 기타 지역 추가 (나머지 65개)
    // 더존종합건설 - 경상도 (25개)
    { id: 'S021', name: '대구 수성 롯데캐슬', company: '종합', address: '대구 수성구 범어동 123', lat: 35.8583, lng: 128.6333, startDate: '2026-03-11', manager: '탁건축', phone: '010-9012-3458', cert: '건축기사', status: '배정완료' },
    { id: 'S022', name: '부산 해운대 힐스테이트', company: '종합', address: '부산 해운대구 중동 456', lat: 35.1628, lng: 129.1639, startDate: '2026-04-07', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'S023', name: '울산 남구 자이', company: '종합', address: '울산 남구 삼산동 789', lat: 35.5389, lng: 129.3300, startDate: '2026-05-18', manager: '허소장', phone: '010-0123-4569', cert: '건축산업기사', status: '배정완료' },
    { id: 'S024', name: '창원 마산 푸르지오', company: '종합', address: '경남 창원시 마산합포구 234', lat: 35.1975, lng: 128.5681, startDate: '2026-03-26', manager: '방현장', phone: '010-1234-5681', cert: '건축기사', status: '배정완료' },
    { id: 'S025', name: '김해 장유 e편한세상', company: '종합', address: '경남 김해시 장유면 567', lat: 35.1833, lng: 128.8111, startDate: '2026-06-12', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'S026', name: '포항 북구 롯데캐슬', company: '종합', address: '경북 포항시 북구 890', lat: 36.0322, lng: 129.3650, startDate: '2026-04-21', manager: '배관리', phone: '010-2345-6782', cert: '건축기사, 안전관리자', status: '배정완료' },
    { id: 'S027', name: '구미 산동 힐스테이트', company: '종합', address: '경북 구미시 산동면 123', lat: 36.1639, lng: 128.3372, startDate: '2026-05-27', manager: '남소장', phone: '010-3456-7893', cert: '건축산업기사', status: '배정완료' },
    { id: 'S028', name: '대구 달서 자이', company: '종합', address: '대구 달서구 월성동 456', lat: 35.8300, lng: 128.5356, startDate: '2026-03-19', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'S029', name: '부산 강서 푸르지오', company: '종합', address: '부산 강서구 명지동 789', lat: 35.1036, lng: 128.9200, startDate: '2026-07-09', manager: '궁현장', phone: '010-4567-8904', cert: '건축기사', status: '배정완료' },
    { id: 'S030', name: '경주 황성 e편한세상', company: '종합', address: '경북 경주시 황성동 234', lat: 35.8378, lng: 129.2114, startDate: '2026-04-14', manager: '석소장', phone: '010-5678-9015', cert: '건축산업기사', status: '배정완료' },
    { id: 'S031', name: '진주 평거 롯데캐슬', company: '종합', address: '경남 진주시 평거동 567', lat: 35.1794, lng: 128.0847, startDate: '2026-05-03', manager: '선관리', phone: '010-6789-0126', cert: '건축기사', status: '배정완료' },
    { id: 'S032', name: '양산 물금 힐스테이트', company: '종합', address: '경남 양산시 물금읍 890', lat: 35.3306, lng: 129.0028, startDate: '2026-03-13', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'S033', name: '거제 장평 자이', company: '종합', address: '경남 거제시 장평동 123', lat: 34.8806, lng: 128.6217, startDate: '2026-06-25', manager: '설소장', phone: '010-7890-1237', cert: '건축산업기사', status: '배정완료' },
    { id: 'S034', name: '통영 무전 푸르지오', company: '종합', address: '경남 통영시 무전동 456', lat: 34.8544, lng: 128.4231, startDate: '2026-04-30', manager: '마현장', phone: '010-8901-2348', cert: '건축기사', status: '배정완료' },
    { id: 'S035', name: '안동 옥동 e편한세상', company: '종합', address: '경북 안동시 옥동 789', lat: 36.5656, lng: 128.7294, startDate: '2026-05-12', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'S036', name: '대구 동구 롯데캐슬', company: '종합', address: '대구 동구 신천동 234', lat: 35.8869, lng: 128.6356, startDate: '2026-03-17', manager: '길관리', phone: '010-9012-3459', cert: '건축기사, 안전관리자', status: '배정완료' },
    { id: 'S037', name: '부산 사상 힐스테이트', company: '종합', address: '부산 사상구 주례동 567', lat: 35.1528, lng: 128.9906, startDate: '2026-06-18', manager: '연소장', phone: '010-0123-4570', cert: '건축산업기사', status: '배정완료' },
    { id: 'S038', name: '울산 동구 자이', company: '종합', address: '울산 동구 일산동 890', lat: 35.5047, lng: 129.4167, startDate: '2026-04-06', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'S039', name: '창원 진해 푸르지오', company: '종합', address: '경남 창원시 진해구 123', lat: 35.1333, lng: 128.7000, startDate: '2026-07-16', manager: '엄현장', phone: '010-1234-5682', cert: '건축기사', status: '배정완료' },
    { id: 'S040', name: '포항 남구 e편한세상', company: '종합', address: '경북 포항시 남구 456', lat: 36.0089, lng: 129.3806, startDate: '2026-05-05', manager: '원소장', phone: '010-2345-6783', cert: '건축산업기사', status: '배정완료' },
    { id: 'S041', name: '김천 삼락 롯데캐슬', company: '종합', address: '경북 김천시 삼락동 789', lat: 36.1397, lng: 128.1139, startDate: '2026-03-21', manager: '좌관리', phone: '010-3456-7894', cert: '건축기사', status: '배정완료' },
    { id: 'S042', name: '거창 가조 힐스테이트', company: '종합', address: '경남 거창군 가조면 234', lat: 35.9978, lng: 127.8981, startDate: '2026-04-27', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'S043', name: '밀양 내이 자이', company: '종합', address: '경남 밀양시 내이동 567', lat: 35.5036, lng: 128.7467, startDate: '2026-06-08', manager: '명소장', phone: '010-4567-8905', cert: '건축산업기사', status: '배정완료' },
    { id: 'S044', name: '사천 용현 푸르지오', company: '종합', address: '경남 사천시 용현면 890', lat: 35.0039, lng: 128.0647, startDate: '2026-05-19', manager: '간현장', phone: '010-5678-9016', cert: '건축기사', status: '배정완료' },
    { id: 'S045', name: '영주 휴천 e편한세상', company: '종합', address: '경북 영주시 휴천동 123', lat: 36.8056, lng: 128.6239, startDate: '2026-03-29', manager: '', phone: '', cert: '', status: '미배정' },

    // 더존하우징 - 경상도 (25개)
    { id: 'H021', name: '대구 북구 더샵', company: '하우징', address: '대구 북구 칠성동 456', lat: 35.8858, lng: 128.5825, startDate: '2026-03-08', manager: '봉건축', phone: '010-6789-0127', cert: '건축기사', status: '배정완료' },
    { id: 'H022', name: '부산 동래 힐스테이트', company: '하우징', address: '부산 동래구 명륜동 789', lat: 35.2044, lng: 129.0789, startDate: '2026-04-13', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'H023', name: '울산 중구 자이', company: '하우징', address: '울산 중구 성남동 234', lat: 35.5694, lng: 129.3317, startDate: '2026-05-24', manager: '기소장', phone: '010-7890-1238', cert: '건축산업기사', status: '배정완료' },
    { id: 'H024', name: '창원 의창 롯데캐슬', company: '하우징', address: '경남 창원시 의창구 567', lat: 35.2536, lng: 128.6481, startDate: '2026-03-15', manager: '복현장', phone: '010-8901-2349', cert: '건축기사', status: '배정완료' },
    { id: 'H025', name: '김해 대동 푸르지오', company: '하우징', address: '경남 김해시 대동면 890', lat: 35.2167, lng: 128.8167, startDate: '2026-06-22', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'H026', name: '포항 흥해 e편한세상', company: '하우징', address: '경북 포항시 북구 흥해읍 123', lat: 36.1083, lng: 129.4333, startDate: '2026-04-24', manager: '란관리', phone: '010-9012-3460', cert: '건축기사, 안전관리자', status: '배정완료' },
    { id: 'H027', name: '구미 옥계 힐스테이트', company: '하우징', address: '경북 구미시 옥계동 456', lat: 36.1394, lng: 128.3572, startDate: '2026-06-01', manager: '목소장', phone: '010-0123-4571', cert: '건축산업기사', status: '배정완료' },
    { id: 'H028', name: '대구 서구 자이', company: '하우징', address: '대구 서구 비산동 789', lat: 35.8717, lng: 128.5583, startDate: '2026-03-27', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'H029', name: '부산 북구 푸르지오', company: '하우징', address: '부산 북구 구포동 234', lat: 35.2047, lng: 128.9950, startDate: '2026-07-14', manager: '민현장', phone: '010-1234-5683', cert: '건축기사', status: '배정완료' },
    { id: 'H030', name: '경산 하양 롯데캐슬', company: '하우징', address: '경북 경산시 하양읍 567', lat: 35.9133, lng: 128.8200, startDate: '2026-04-17', manager: '두소장', phone: '010-2345-6784', cert: '건축산업기사', status: '배정완료' },
    { id: 'H031', name: '진주 금산 힐스테이트', company: '하우징', address: '경남 진주시 금산면 890', lat: 35.1306, lng: 128.1594, startDate: '2026-05-09', manager: '장관리', phone: '010-3456-7895', cert: '건축기사', status: '배정완료' },
    { id: 'H032', name: '양산 중부 자이', company: '하우징', address: '경남 양산시 중부동 123', lat: 35.3397, lng: 129.0378, startDate: '2026-03-23', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'H033', name: '거제 옥포 푸르지오', company: '하우징', address: '경남 거제시 옥포동 456', lat: 34.8953, lng: 128.6842, startDate: '2026-06-29', manager: '서소장', phone: '010-4567-8906', cert: '건축산업기사', status: '배정완료' },
    { id: 'H034', name: '통영 도남 e편한세상', company: '하우징', address: '경남 통영시 도남동 789', lat: 34.8478, lng: 128.4344, startDate: '2026-05-02', manager: '문현장', phone: '010-5678-9017', cert: '건축기사', status: '배정완료' },
    { id: 'H035', name: '안동 태화 롯데캐슬', company: '하우징', address: '경북 안동시 태화동 234', lat: 36.5683, lng: 128.7347, startDate: '2026-04-09', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'H036', name: '대구 남구 힐스테이트', company: '하우징', address: '대구 남구 대명동 567', lat: 35.8467, lng: 128.5944, startDate: '2026-03-31', manager: '전관리', phone: '010-6789-0128', cert: '건축기사, 안전관리자', status: '배정완료' },
    { id: 'H037', name: '부산 연제 자이', company: '하우징', address: '부산 연제구 연산동 890', lat: 35.1833, lng: 129.0800, startDate: '2026-06-26', manager: '최소장', phone: '010-7890-1239', cert: '건축산업기사', status: '배정완료' },
    { id: 'H038', name: '울산 울주 푸르지오', company: '하우징', address: '울산 울주군 삼남읍 123', lat: 35.5386, lng: 129.2422, startDate: '2026-04-11', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'H039', name: '창원 성산 e편한세상', company: '하우징', address: '경남 창원시 성산구 456', lat: 35.2181, lng: 128.6808, startDate: '2026-07-19', manager: '전현장', phone: '010-8901-2350', cert: '건축기사', status: '배정완료' },
    { id: 'H040', name: '포항 청림 롯데캐슬', company: '하우징', address: '경북 포항시 남구 청림동 789', lat: 36.0194, lng: 129.3656, startDate: '2026-05-13', manager: '곽소장', phone: '010-9012-3461', cert: '건축산업기사', status: '배정완료' },
    { id: 'H041', name: '김천 율곡 힐스테이트', company: '하우징', address: '경북 김천시 율곡동 234', lat: 36.1200, lng: 128.1350, startDate: '2026-03-25', manager: '팽관리', phone: '010-0123-4572', cert: '건축기사', status: '배정완료' },
    { id: 'H042', name: '거창 신원 자이', company: '하우징', address: '경남 거창군 신원면 567', lat: 35.8394, lng: 127.8706, startDate: '2026-05-01', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'H043', name: '밀양 삼랑 푸르지오', company: '하우징', address: '경남 밀양시 삼랑진읍 890', lat: 35.2981, lng: 128.8131, startDate: '2026-06-14', manager: '소소장', phone: '010-1234-5684', cert: '건축산업기사', status: '배정완료' },
    { id: 'H044', name: '사천 사남 e편한세상', company: '하우징', address: '경남 사천시 사남면 123', lat: 35.0725, lng: 128.0544, startDate: '2026-05-26', manager: '당현장', phone: '010-2345-6785', cert: '건축기사', status: '배정완료' },
    { id: 'H045', name: '영주 가흥 롯데캐슬', company: '하우징', address: '경북 영주시 가흥동 456', lat: 36.8200, lng: 128.6367, startDate: '2026-04-02', manager: '', phone: '', cert: '', status: '미배정' },
    
    // 전라도 및 기타 지역 (15개)
    { id: 'S046', name: '광주 수완 힐스테이트', company: '종합', address: '광주 광산구 수완동 789', lat: 35.1792, lng: 126.8192, startDate: '2026-03-09', manager: '송건축', phone: '010-3456-7896', cert: '건축기사', status: '배정완료' },
    { id: 'S047', name: '전주 덕진 자이', company: '종합', address: '전북 전주시 덕진구 234', lat: 35.8494, lng: 127.1361, startDate: '2026-04-15', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'S048', name: '목포 하당 푸르지오', company: '종합', address: '전남 목포시 하당동 567', lat: 34.7939, lng: 126.3892, startDate: '2026-05-21', manager: '엄소장', phone: '010-4567-8907', cert: '건축산업기사', status: '배정완료' },
    { id: 'S049', name: '여수 여서 롯데캐슬', company: '종합', address: '전남 여수시 여서동 890', lat: 34.7604, lng: 127.6622, startDate: '2026-03-18', manager: '연현장', phone: '010-5678-9018', cert: '건축기사', status: '배정완료' },
    { id: 'S050', name: '순천 조례 e편한세상', company: '종합', address: '전남 순천시 조례동 123', lat: 34.9506, lng: 127.4872, startDate: '2026-06-17', manager: '', phone: '', cert: '', status: '미배정' },
    
    { id: 'H046', name: '광주 첨단 힐스테이트', company: '하우징', address: '광주 광산구 첨단동 456', lat: 35.2256, lng: 126.8444, startDate: '2026-03-12', manager: '옹관리', phone: '010-6789-0129', cert: '건축기사, 안전관리자', status: '배정완료' },
    { id: 'H047', name: '전주 송천 자이', company: '하우징', address: '전북 전주시 덕진구 송천동 789', lat: 35.8628, lng: 127.1253, startDate: '2026-04-18', manager: '', phone: '', cert: '', status: '미배정' },
    { id: 'H048', name: '목포 연산 푸르지오', company: '하우징', address: '전남 목포시 연산동 234', lat: 34.8069, lng: 126.3972, startDate: '2026-05-28', manager: '제소장', phone: '010-7890-1240', cert: '건축산업기사', status: '배정완료' },
    { id: 'H049', name: '여수 문수 롯데캐슬', company: '하우징', address: '전남 여수시 문수동 567', lat: 34.7358, lng: 127.7422, startDate: '2026-03-20', manager: '갈현장', phone: '010-8901-2351', cert: '건축기사', status: '배정완료' },
    { id: 'H050', name: '순천 연향 e편한세상', company: '하우징', address: '전남 순천시 연향동 890', lat: 34.9631, lng: 127.4925, startDate: '2026-06-24', manager: '', phone: '', cert: '', status: '미배정' },
    
    // 추가 현장 175개 (S051-S125, H051-H125) - 간략화를 위해 패턴만 표시
    // 실제로는 이 부분에 175개의 현장 데이터를 더 추가해야 합니다
];

// 225개 전체 생성을 위한 자동 생성 로직
function generateAllSites() {
    const cities = [
        { name: '평택', lat: 36.9921, lng: 126.9730 },
        { name: '수원', lat: 37.2636, lng: 127.0286 },
        { name: '용인', lat: 37.2639, lng: 127.1483 },
        { name: '화성', lat: 37.2000, lng: 127.0750 },
        { name: '성남', lat: 37.3944, lng: 127.1110 },
        { name: '안양', lat: 37.3894, lng: 126.9511 },
        { name: '부천', lat: 37.4989, lng: 126.7658 },
        { name: '광명', lat: 37.4778, lng: 126.8650 },
        { name: '시흥', lat: 37.3806, lng: 126.8031 },
        { name: '안산', lat: 37.3189, lng: 126.8300 },
    ];
    
    const projectTypes = ['푸르지오', '힐스테이트', '자이', '롯데캐슬', 'e편한세상', '더샵', '센트럴'];
    const managers = ['김현장', '이소장', '박건설', '최관리', '정현장', '강소장', '윤현장', '임건축', '한소장', '송현장'];
    const officeStaff = ['박사무실장', '최사무실', '강사무직원', '김사무직원', '이사무실', '정직원', '한직원', '윤사원'];
    const certs = ['건축기사', '건축산업기사', '건축기사, 안전관리자'];
    const statuses = ['건축허가', '착공예정', '착공중'];
    const specialNotesList = ['대단지 개발', '역세권', '학군지', '재개발 사업', '신도시', '도심형', '브랜드 단지', '교통 편리'];
    
    // 기존 15개에 추가로 210개 생성
    for (let i = sitesData.length; i < 225; i++) {
        const isJonghap = i % 2 === 0;
        const company = isJonghap ? '종합' : '하우징';
        const prefix = isJonghap ? 'S' : 'H';
        const cityIndex = i % cities.length;
        const city = cities[cityIndex];
        const projectType = projectTypes[i % projectTypes.length];
        const hasManager = Math.random() > 0.3; // 70% 확률로 소장 배정
        
        const permitYear = 2025 + Math.floor(Math.random() * 2);
        const permitMonth = Math.floor(Math.random() * 12) + 1;
        const permitDay = Math.floor(Math.random() * 28) + 1;
        
        const startYear = 2026;
        const startMonth = Math.floor(Math.random() * 12) + 1;
        const startDay = Math.floor(Math.random() * 28) + 1;
        
        const completionYear = 2027 + Math.floor(Math.random() * 2);
        const completionMonth = Math.floor(Math.random() * 12) + 1;
        const completionDay = Math.floor(Math.random() * 28) + 1;
        
        const managerName = hasManager ? managers[i % managers.length] : '';
        const useCertFromOffice = !hasManager || Math.random() > 0.5; // 50% 확률로 사무직원 자격증 사용
        
        sitesData.push({
            id: `${prefix}${String(Math.floor(i / 2) + 1).padStart(3, '0')}`,
            name: `${city.name} ${projectType} ${i}`,
            company: company,
            address: `${city.name}시 ${i}번지`,
            lat: city.lat + (Math.random() - 0.5) * 0.1,
            lng: city.lng + (Math.random() - 0.5) * 0.1,
            permitDate: `${permitYear}-${String(permitMonth).padStart(2, '0')}-${String(permitDay).padStart(2, '0')}`,
            startDate: `${startYear}-${String(startMonth).padStart(2, '0')}-${String(startDay).padStart(2, '0')}`,
            completionDate: `${completionYear}-${String(completionMonth).padStart(2, '0')}-${String(completionDay).padStart(2, '0')}`,
            siteStatus: statuses[i % statuses.length],
            specialNotes: specialNotesList[i % specialNotesList.length],
            manager: managerName,
            managerPhone: hasManager ? `010-${Math.floor(Math.random() * 9000) + 1000}-${Math.floor(Math.random() * 9000) + 1000}` : '',
            certName: certs[i % certs.length],
            certOwner: useCertFromOffice ? officeStaff[i % officeStaff.length] : managerName || officeStaff[i % officeStaff.length],
            certPhone: useCertFromOffice ? `010-${Math.floor(Math.random() * 9000) + 1000}-${Math.floor(Math.random() * 9000) + 1000}` : 
                       (hasManager ? `010-${Math.floor(Math.random() * 9000) + 1000}-${Math.floor(Math.random() * 9000) + 1000}` : `010-${Math.floor(Math.random() * 9000) + 1000}-${Math.floor(Math.random() * 9000) + 1000}`),
            completionCertFile: null,
            status: hasManager ? '배정완료' : '미배정'
        });
    }
}

// 225개 전체 생성 실행
generateAllSites();
