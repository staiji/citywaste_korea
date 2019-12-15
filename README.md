# Home Assistant CityWaste Korea Component

This is a citywaste.or.kr sensor component for Home Assistant. (https://www.citywaste.or.kr)

### Installation

Copy this folder to `<config_dir>/custom_components/citywaste_korea/`.

Add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
sensor:
  platform: citywaste_korea
  tagprintcd: KKRW0B1C000000000
  aptdong: 101
  apthono: 1004
```

- tagprintcd: RFID 태그 인쇄번호 입력
- aptdong: 동 입력
- apthono: 호 입력
- 조회기간은 이번달 1일부터 오늘까지 입니다.
- 정보를 가져오는 주기는 최소 30분 입니다.
- https://www.citywaste.or.kr/portal/status/selectSimpleEmissionQuantity.do 페이지에서 태그 인쇄번호와 동, 호를 입력해 정상적으로 조회가 되는지 확인후 사용해 주세요
