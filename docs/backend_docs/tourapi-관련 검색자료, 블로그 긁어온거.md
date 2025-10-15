TourAPI 사용법

TourAPI
한국 관광지 정보를 OpenAPI로 제공해준다.

OpenAPI 활용신청방법
https://api.visitkorea.or.kr/openAPI/applicationGuide.do
관광데이터는 다국어서비스를 제공해주지만 국문에 대한 방법만 알아보자!

REST방식 URL 요청하기
어떤 정보를 조회하든 기본적으로 들어가는 파라미터들을 먼저 정리해보자
요청 메시지

numOfRows : 한 페이지 결과 수
pageNo : 페이지 번호
MobileOS : OS 구분(IOS, AND, WIN)(_)
MobileApp : 서비스 명 = 어플 명(_)
ServiceKey : 인증 키(\*)
응답 메시지

resultCode : 결과코드
resultMsg : 결과메시지(ex: OK)
numOfRows : 한 페이지 결과 수
pageNum : 페이지 번호
totalCount : 전체 결과 수
이 파라미터는 기본으로 사용한다.
(\*)표시는 필수입력 정보이다.

지역코드 조회
지역코드, 시군구코드 목록을 조회하는 기능이다.

요청 메시지

areaCode : 지역코드, 시군구코드
응답 메시지

code : 지역코드, 시군구코드
name : 지역명, 시군구명
rnum : 일련번호
예시 URL

http://api.visitkorea.or.kr/openapi/service/rest/EngService/areaCode?serviceKey=인증키&numOfRows=10&pageSize=10&pageNo=1&MobileOS=ETC&MobileApp=AppTest
응답 표준은 XML이며, JSON형식을 요청받고 싶은 경우 "&\_type=json"을 추가하면 된다. 다른 형식은 제공하지 않는다.

결과화면

enter image description here

지역기반 관광정보 조회
https://api.visitkorea.or.kr/guide/inforArea.do](https://api.visitkorea.or.kr/guide/inforArea.do)
여기를 참고하면 어떤 URL을 입력하면 되는지 알 수 있다.

관광타입 - 관광지, 지역 - 서울>동대문구는 다음과 같은 URL로 요청하면 된다. 파라미터에 따라 제목순, 수정일순, 등록일순, 인기순으로 정렬검색 기능도 제공한다.

[http://api.visitkorea.or.kr/openapi/service/rest/KorService/areaBasedList?ServiceKey=인증키&contentTypeId=12&areaCode=1&sigunguCode=11&cat1=&cat2=&cat3=&listYN=Y&MobileOS=ETC&MobileApp=TourAPI3.0_Guide&arrange=A&numOfRows=12&pageNo=1]
요청메시지

listYN : 목록 구분(Y=목록, N=개수)
arrange : 정렬구분
(A=제목순, B=조회순, C=수정일순, D=생성일순)
대표이미지가 반드시 있는 정렬(O=제목순, P=조회순, Q=수정일순, R=생성일순)
contentTypeId : 관광타입(관광지, 숙박 등)ID
areaCode : 지역코드
singunguCode : 시군구코드(areacode필수)
cat1, cat2, cat3: 대분류>중분류>소분류
listYN = N경우 : 개수만 출력해준다

listYN = Y인 경우 : 목록 출력

addr1 : 주소(ex: 서울 중구 다동)
addr : 상세주소
areacode
cat1,cat2,cat3
contentid
contettypeid : 관광지타입id
createdtime : 등록일
firstimage : 대표이미지원본(약 500*333 size)
firstimage2 : 대표이미지사본(약 150*150 size)
mapx : GPS X좌표 (경도)
mapy : GPS Y좌표 (위도)
mlevel : Map Level
modifiedtime
readcount : 조회수
sigungucode
tel
title
zipcode : 우편번호
인증키에는 발급받은 인증키를 넣고 해당 URL로 들어가면
enter image description here

이외에도 위치기반검색, 키워드 검색등 다양한 정보를 제공해준다.

JSON 응답 예시
{
"response": {
"header": {
"resultCode": "00",
"resultMsg": "정상"
},
"body": {
"items": [
{
"code": "11110",
"name": "서울특별시",
"rnum": 1
},
{
"code": "11120",
"name": "부산광역시",
"rnum": 2
},
...
],
"numOfRows": 10,
"pageNo": 1,
"totalCount": 100
}
}
}
