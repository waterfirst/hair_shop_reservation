# 미용실 예약 시스템

이 프로젝트는 미용실을 위한 간단한 웹 기반 예약 시스템입니다. 특히 나이 든 분들이 쉽게 사용할 수 있도록 큰 폰트와 간단한 UI로 설계되었습니다.

![미용실 예약 시스템 스크린샷](https://via.placeholder.com/800x400?text=미용실+예약+시스템)

## 주요 기능

- 날짜 선택 (일주일 단위로 표시, 일요일 휴무)
- 시간대별 예약 가능 여부 확인
- 컷(1시간)과 펌(2시간) 서비스 예약
- 예약 충돌 방지 시스템
- 사용자 친화적인 인터페이스
- 예약 목록 확인 및 관리
- 최근 예약 내역 확인

## 데모

[라이브 데모 링크](#) (준비 중)

## 설치 방법

1. 저장소 클론:
```bash
git clone https://github.com/waterfirst/hair_shop_reservation.git
cd hair_shop_reservation
```

2. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

3. 애플리케이션 실행:
```bash
python app.py
```

4. 웹 브라우저에서 다음 주소로 접속:
```
http://127.0.0.1:5000/
```

## 사용 방법

1. 메인 페이지에서 원하는 날짜를 선택합니다.
2. 선택한 날짜의 가능한 시간대를 확인합니다.
3. 원하는 시간대와 서비스(컷 또는 펌)를 선택합니다.
4. 이름과 전화번호를 입력하여 예약을 완료합니다.
5. 메인 페이지나 예약 목록 페이지에서 예약 내역을 확인할 수 있습니다.

## 기술 스택

- Python 3.x
- Flask
- SQLite
- HTML/CSS/JavaScript
- 반응형 디자인

## 프로젝트 구조

```
hair_shop_reservation/
├── app.py                  # 메인 애플리케이션 파일
├── requirements.txt        # 의존성 패키지 목록
├── salon.db                # SQLite 데이터베이스
└── templates/              # HTML 템플릿
    ├── base.html           # 기본 레이아웃
    ├── index.html          # 메인 페이지
    ├── appointments.html   # 예약 시간 선택 페이지
    └── appointment_list.html # 예약 목록 페이지
```

## 확장 가능성

- 사용자 인증 시스템 추가
- 관리자 페이지 구현
- 예약 알림 기능
- 디자이너 선택 기능
- 온라인 결제 시스템 연동

## 기여 방법

1. 이 저장소를 포크합니다.
2. 새 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`).
3. 변경 사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`).
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`).
5. Pull Request를 생성합니다.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 연락처

프로젝트 관리자: [GitHub 프로필](https://github.com/waterfirst)

프로젝트 링크: [https://github.com/waterfirst/hair_shop_reservation](https://github.com/waterfirst/hair_shop_reservation) 