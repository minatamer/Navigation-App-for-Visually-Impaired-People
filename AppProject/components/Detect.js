import { Camera, CameraType } from "expo-camera";
import { useState, useEffect, useRef } from "react";
import { Svg, Rect } from "react-native-svg";
import {
  Button,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  Vibration,
} from "react-native";
import * as Speech from "expo-speech";
import { Audio } from "expo-av";
import * as FileSystem from "expo-file-system";
import { Asset } from "expo-asset";

export default function Detect() {
  const [permission, requestPermission] = Camera.useCameraPermissions();
  const cameraRef = useRef(null);
  const [boundingBoxes, setBoundingBoxes] = useState([]);
  const [flashMode, setFlashMode] = useState(Camera.Constants.FlashMode.off);
  const [sound, setSound] = useState();
  const [language, setLanguage] = useState('');

  async function playSound() {
    try {
      const sourcePath =
        "C:/Users/Mina/Desktop/bachelor/Navigation-App-for-Visually-Impaired-People/AppProject/output.mp3";
      const { sound } = await Audio.Sound.createAsync(require(sourcePath));
      setSound(sound);
      await sound.playAsync();
      setSound();
    } catch (error) {
      console.error("Error:", error);
    }
  }

  const startRecording = async () => {
    console.log("started recording");
    if (cameraRef.current) {
      try {
        const video = await cameraRef.current.recordAsync({
          maxDuration: 3,
          quality: "4:3",
        });
        console.log("Video recorded at:", video.uri);
        sendVideoToBackend(video);
      } catch (error) {
        console.log("Failed to record video:", error);
      }
    }
  };

  //Force a delay before calling function to let the page load first
  useEffect(() => {
    // Vibration.vibrate(2000);
    Speech.speak(`Do you want Arabic language?`);
    const timeoutId = setTimeout(() => {

      if (language === ''){
        startRecording();
      }
    }, 3000);
    return () => {
      Speech.stop();
    }; //Stop speech on unmount
  }, []);

  useEffect(() => {
    captureFrame();
  }, [language]);

  const handleSpeak = (distance, className) => {
    //English Speech
    if (language === "english"){
      Speech.speak(`A ${className} is ${distance.toFixed(1)} centimeters away.`);
    }
    else {
      //Arabic Speech
      playSound();
    }
  };

  const captureFrame = async () => {
    if (cameraRef.current) {
      let photo = await cameraRef.current.takePictureAsync({
        quality: 0.2,
      });
      sendDataToBackend(photo);
    }
  };

  const sendDataToBackend = async (photo) => {
    const startTime = new Date();
    const formData = new FormData();
    formData.append("image", {
      uri: photo.uri,
      type: "image/jpeg",
      name: "photo.jpg",
    });
    try {
      const response = await fetch("http://192.168.1.15:8080/camera", {
        method: "POST",
        body: formData,
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      const data = await response.json();

      const endTime = new Date();
      const duration = endTime - startTime;
      console.log("Request duration:", duration, "ms");
      console.log("Response from backend:", data);

      if (data.length === 0) {
        setFlashMode(Camera.Constants.FlashMode.torch);
      } else {
        setFlashMode(Camera.Constants.FlashMode.off);
        let isSpeaking = await Speech.isSpeakingAsync();
        for (const box of data) {
          if (language === "english"){
            if (box.distance < 50  && !isSpeaking) {
              handleSpeak(box.distance, box.class);
            }
          }
          else{
            if (box.distance < 50 && box.arabic === "yes") {
              setTimeout(() => {
                handleSpeak(box.distance, box.class);
              }, 1000);
              break;
            }
          }
        }
      }

      setBoundingBoxes(data);
    } catch (error) {
      console.error("Error sending data to backend:", error);
      setBoundingBoxes([]);
    }

    captureFrame();
    captureFrame();
  };


  const sendVideoToBackend = async (video) => {
    const startTime = new Date();
    const formData = new FormData();
    formData.append("video", {
      uri: video.uri,
      type: "video/mp4",
      name: "video.mp4",
    });
    try {
      const response = await fetch("http://192.168.1.15:8080/video", {
        method: "POST",
        body: formData,
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      const data = await response.json();
      const endTime = new Date();
      const duration = endTime - startTime;
      console.log("Request duration:", duration, "ms");
      console.log("Response from backend:", data);
      // if (data.includes("switch") || data.includes("language")) {
      //   if (language === "english"){
      //     console.log('Switching Langauge to Arabic');
      //     setLanguage('arabic');
      //   }
      //   else{
      //     console.log('Switching Langauge to English');
      //     setLanguage('english');
      //   }
      // }

      if (data === false) {
          console.log('Setting Langauge to Arabic');
          setLanguage('arabic');
        }
        else{
          console.log('Setting Langauge to English');
          setLanguage('english');
      }
      

    } catch (error) {
      console.log("Error sending video to backend:", error);
    }

  };



  if (!permission) {
    // Camera permissions are still loading
    return <View />;
  }

  if (!permission.granted) {
    // Camera permissions are not granted yet
    return (
      <View style={styles.container}>
        <Text style={{ textAlign: "center" }}>
          We need your permission to show the camera
        </Text>
        <Button onPress={requestPermission} title="grant permission" />
      </View>
    );
  }
  const onCameraReady = async () => {
    if (cameraRef.current) {
      const size = await cameraRef.current.getAvailablePictureSizesAsync("4:3");
      console.log(size);
    }
  };

  return (
    <View style={styles.container}>
      <Camera
        style={styles.camera}
        flashMode={flashMode}
        type={Camera.Constants.Type.back}
        ref={cameraRef}
      >
        <View style={styles.buttonContainer}>
          <Svg style={styles.svg}>
            {boundingBoxes.map((box, index) => (
              <Rect
                key={`rect-${index}`}
                x={box.x}
                y={box.y}
                width={box.width}
                height={box.height}
                fill="transparent"
                stroke="green"
                strokeWidth="2"
              />
            ))}
            {boundingBoxes.map((box, index) => (
              <Text
                key={`text-${index}`}
                fontSize="16"
                style={{
                  color: "green",
                  paddingTop: box.y,
                  paddingLeft: box.x,
                }}
              >
                {box.class} {"\n"}Distance:{" "}
                {parseFloat(box.distance.toFixed(1))} cm
              </Text>
            ))}
          </Svg>
        </View>
      </Camera>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
  },
  camera: {
    flex: 1,
  },
  buttonContainer: {
    flex: 1,
    flexDirection: "row",
    backgroundColor: "transparent",
    margin: 64,
  },
  button: {
    flex: 1,
    alignSelf: "flex-end",
    alignItems: "center",
  },
  text: {
    fontSize: 24,
    fontWeight: "bold",
    color: "white",
  },
});
