// This code was written by Juhyun Kim.

// GPS좌표 및 위치 리음 설정
let lat = 0;
let long = 0;
let label = "쥬디다무 집"

// Firebase 접근 정보
var config = {
  apiKey: "AIzaSyDl63L5STtT61W-8rS9kBu5lGMi-psb9BQ",
  authDomain: "test-ac43f.firebaseapp.com",
  databaseURL: "https://test-ac43f-default-rtdb.firebaseio.com",
  projectId: "test-ac43f",
  storageBucket: "test-ac43f.appspot.com",
  messagingSenderId: "27807043520",
  appId: "1:27807043520:web:0f996bf9f38eeba9be8225"
};
firebase.initializeApp(config);
database = firebase.database();


// 지도 정보 가져오기
function initMap() {
  // 위치 정보 가져오기
  var refLocation = database.ref("location");
  refLocation.on("value", gotLocation, errData);

  function gotLocation(data) {
    // console.log(data.val());
    // console.log(data.val()["lat"])
    // console.log(data.val()["long"])
    lat = data.val()["lat"]
    long = data.val()["long"]

    // console.log(lat, long)
    var seoul = { lat: lat, lng: long };
    var map = new google.maps.Map(
      document.getElementById('map'), {
        zoom: 12,
        center: seoul
      });

      new google.maps.Marker({
      position: seoul,
      map: map,
      label: label
    });
  }

  function errData(err) {
    console.log("Error!");
    console.log(err);
  }
}
