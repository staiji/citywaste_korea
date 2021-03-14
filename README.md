# Home Assistant CityWaste Korea Component (음식물 쓰레기 배출량 조회)

This is a citywaste.or.kr sensor component for Home Assistant. (https://www.citywaste.or.kr)

![citywaste_readme](https://user-images.githubusercontent.com/54183150/111070275-595c6680-8514-11eb-9979-ea1bd6c214d0.jpg)

### Installation
#### 1. Component 추가
1.1 HACS 사용시

``HACS -> integrations -> 우상단 점세개 -> custom repository -> Add custom repository URL에 https://github.com/staiji/citywaste_korea 입력 -> Category에서  integration 선택 -> ADD -> Install ``
 
1.2 HACS 미사용시 다운로드 받은 파일을 `<config_dir>/custom_components/citywaste_korea/` 위치에 직접 복사

```
├── automations.yaml
├── configuration.yaml
├── custom_components
│   ├── citywaste_korea
│   │   ├── LICENSE
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.json
│   │   └── sensor.py
│   └── hacs
│       ├── __init__.py
```

#### 2. `configuration.yaml` 파일에 다음 설정 추가

```yaml
# Example configuration.yaml entry
sensor:
  - platform: citywaste_korea
    tagprintcd: KKRW0B1C000000000
    aptdong: 101
    apthono: 1004
```

- tagprintcd: RFID 태그 인쇄번호 입력
- aptdong: 동 입력
- apthono: 호 입력
- 조회기간은 이번달 1일부터 오늘까지 입니다.
- 정보를 가져오는 주기는 최소 30분 입니다.
- https://www.citywaste.or.kr/portal/status/selectSimpleEmissionQuantity.do 페이지에서 태그 인쇄번호와 동, 호를 입력해 정상적으로 조회가 되는지 확인 후 사용해 주세요
