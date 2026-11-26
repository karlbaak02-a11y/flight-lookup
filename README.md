# Flight Lookup Offline v1.0

아이폰·아이패드·Android·PC에서 사용할 수 있는 오프라인 편명 검색 PWA. 실제 DB는 GitHub Actions가 Virtual Radar Server standing-data(CC0)를 내려받아 구축합니다. 이 배포본에는 실제 전체 DB가 포함되지 않습니다. 예제 테스트 버튼은 3개 시연용 레코드만 표시하며 저장하거나 실제 DB로 간주하지 않습니다.

## 최초 설치 (GitHub 계정 필요, 공개 저장소 기준 무료)

1. https://github.com/new 에서 Public 저장소를 생성합니다. 이름 예: `flight-lookup`. README 자동 추가는 선택 사항입니다. 기본 브랜치는 `main`으로 사용합니다.
2. ZIP을 해제하고 내부 `.github`, `scripts`, `site`, `README.md`를 저장소 루트에 올립니다. GitHub 웹의 Add file → Upload files에서 폴더 구조를 유지하세요. Mac Finder에서 숨김 폴더 `.github`가 안 보이면 `Command+Shift+.`를 누릅니다. 웹 업로드가 숨김 폴더를 누락하면 GitHub 웹에서 Add file → Create new file로 `.github/workflows/pages.yml`을 만들고 제공 파일의 내용을 그대로 붙여넣습니다. ZIP 자체를 올리는 것이 아닙니다. 또는 GitHub Desktop/git을 사용합니다.
3. 저장소 Settings → Pages → Build and deployment → Source에서 **GitHub Actions**를 선택합니다.
4. Actions → Build and publish Flight Lookup → Run workflow → main → Run workflow. 성공하면 Settings → Pages 또는 Actions 배포 결과에 사이트 주소가 표시됩니다. 첫 실행이 Settings 설정 전 실패한 경우 다시 실행합니다. 자동 실행은 매일 한국시간 03:17 예정이며 GitHub의 큐나 정책으로 늦어지거나 중단될 수 있습니다. 60일간 저장소 활동이 없는 공개 저장소에서는 예약 워크플로가 비활성화될 수 있으므로 Actions에서 확인합니다.
5. 아이폰 Safari에서 해당 주소를 열고 첫 DB 다운로드가 끝날 때까지 기다립니다. 공유 → 홈 화면에 추가 → 추가. 홈 화면 아이콘에서 다시 열어 **오프라인 준비 완료** 표시를 확인합니다. 홈 화면 앱과 Safari의 저장소가 분리될 수 있으므로 반드시 홈 화면 앱에서 확인합니다.
6. 비행기 모드를 켜고 Wi-Fi도 끈 다음 앱을 완전히 종료하고 홈 화면에서 재실행합니다. 여러 편명을 검색해 확인합니다. DB 백업 버튼을 눌러 파일 앱의 '나의 iPhone'에 JSON을 저장할 수 있습니다. 백업은 DB만 포함하므로 앱 자체 캐시까지 복구하려면 온라인에서 앱을 다시 설치해야 할 수 있습니다.

## 사용

- KAL81, KAL081, KE81, KE081처럼 입력하면 정확히 일치하는 결과 우선. 정확히 일치하지 않으면 접두어 부분 검색. 항공사 코드만으로 검색도 가능.
- 숫자 뒤 알파벳이 붙는 콜사인도 원문 검색. IATA 환산은 원본 Number가 숫자 또는 숫자+문자일 때 항공사 IATA 코드와 조합. 실제 판매 편명·공동운항 번호와 일치하지 않을 수 있습니다.
- 복수 노선과 중간 경유 구간은 별도 표시합니다. 날짜별 실제 운항은 판별하지 않습니다.
- 앱이 열려 있고 온라인이면 마지막 성공 확인 후 24시간 경과 시 갱신합니다. 수동 DB 업데이트 가능. 검색은 네트워크를 사용하지 않습니다. 백그라운드에서 자동 다운로드를 보장하지 않습니다.
- 새 DB를 검증한 뒤 IndexedDB에 하나의 트랜잭션으로 교체합니다. 오류·대폭 감소·구버전이면 기존 정상 DB를 유지합니다. 저장에 실패하면 기존 정상 DB를 유지하거나(없을 경우) 임시 메모리 모드로 표시합니다.
- 로컬 HTML은 화면 테스트용이며 DB 가져오기를 지원하지만 파일 URL에서는 브라우저가 저장소 접근을 제한할 수 있습니다. 실제 오프라인 홈 화면 사용은 HTTPS 배포가 필요합니다.

## 데이터 및 한계

Source: https://github.com/vradarserver/standing-data (CC0-1.0). Community-maintained reference routes, not verified flight schedules. 일부 편명과 항공사·공항 정보는 누락 또는 과거 데이터일 수 있습니다. 주요 항공사만 한글명을 표시하며 나머지는 영문명입니다. 실시간 위치·회항·목적지 변경·운항 여부는 확인하지 않습니다. 운항 판단용으로 사용하지 마세요.

## 개발 / 자체 서버

Python 3 표준 라이브러리만 사용합니다. upstream 저장소를 clone(airlines/schema-01, airports/schema-01, routes/schema-01 경로 포함)한 뒤 `python3 scripts/build_db.py upstream site` 실행. `site/`를 HTTPS 정적 서버에 배포합니다. `python3 -m http.server 8000 --directory site`로 localhost에서 개발 테스트할 수 있습니다. Service Worker를 수정하면 sw.js의 CACHE 버전을 올려야 합니다.

## 검증 범위

작성 환경에서 upstream 호스트 DNS 접속이 불가하여 전체 원본 DB 다운로드와 실제 GitHub 배포는 수행하지 못했습니다. 공개된 노선·공항 CSV 스키마에 맞추었고, 항공사 헤더는 여러 이름에 대응하도록 구성했습니다. JS 구문 및 합성 CSV 빌드·검색 인덱스 테스트를 실행했습니다. 실제 iOS 기기 테스트와 실제 전체 데이터의 완전성은 아직 확인되지 않았습니다.
