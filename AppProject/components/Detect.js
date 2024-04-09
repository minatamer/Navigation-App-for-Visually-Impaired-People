import { Camera, CameraType } from 'expo-camera';
import { useState, useEffect , useRef} from 'react';
import { Svg, Rect } from 'react-native-svg';
import { Button, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import * as Speech from "expo-speech";

export default function Detect() {
  const [permission, requestPermission] = Camera.useCameraPermissions();
  const cameraRef = useRef(null);
  const [boundingBoxes, setBoundingBoxes] = useState([]);
  const [flashMode, setFlashMode] = useState(Camera.Constants.FlashMode.off);
  const [isSpeaking, setIsSpeaking] = useState(false);

  //Force a delay before calling function to let the page load first
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      captureFrame();
    }, 500);
    return () =>{ Speech.stop();}; //Stop speech on unmount
  }, []);


  const handleSpeak = (distance, className) => {
    console.log('SPEAKING STATE ' + isSpeaking);
    Speech.speak(`A ${className} is ${distance.toFixed(1)} centimeters away.`);
  };

  const debouncedHandleSpeak = (distance, className) => {
    clearTimeout(debounceTimer); 
    const timer = setTimeout(() => {
      handleSpeak(distance, className); 
    }, 4000); 
    setDebounceTimer(timer); 
  };

//   useEffect(() => {
//     const intervalId = setInterval(() => {
//       captureFrame();
//     }, 1000);
//     return () => {
//         clearInterval(intervalId);
//     };
// }, []);


  const captureFrame = async () => {
    if (cameraRef.current) {
      let photo = await cameraRef.current.takePictureAsync({
        quality: 0.2
      });
      // const manipResult = await ImageManipulator.manipulateAsync(
      //   uri,
      //   [{ resize: { width : 480, height : 640 } }],
      //   { compress: 1, format: ImageManipulator.SaveFormat.JPEG }
      // );
      sendDataToBackend(photo);

    }
  };


  const sendDataToBackend = async (photo) => {
    const startTime = new Date();
    var dataArray = null;
  const formData = new FormData();
  formData.append('image', {
    uri: photo.uri,
    type: 'image/jpeg', 
    name: 'photo.jpg' 
  });
  fetch('http://192.168.1.15:8081/camera', {
    method: 'POST',
    body: formData,
    headers: {
      'Content-Type': 'application/json',
      "Content-Type": "multipart/form-data",
    },
  })
    .then(response => response.json())
    .then(data => {
      const endTime = new Date();
      const duration = endTime - startTime; 
      console.log('Request duration:', duration, 'ms');
      console.log('Response from backend:', data);
      if (data.length ===0){
        setFlashMode(Camera.Constants.FlashMode.torch);
      }
      else{
        for (const box of data) {
          if (box.distance < 50) {
            handleSpeak(box.distance, box.class);
            break;
          }
        }
      }
      setBoundingBoxes(data);
    })
    .catch(error => {
      // console.error('Error sending data to backend:', error);
      setBoundingBoxes([]);
    });
    captureFrame();
};

  if (!permission) {
    // Camera permissions are still loading
    return <View />;
  }

  if (!permission.granted) {
    // Camera permissions are not granted yet
    return (
      <View style={styles.container}>
        <Text style={{ textAlign: 'center' }}>We need your permission to show the camera</Text>
        <Button onPress={requestPermission} title="grant permission" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Camera style={styles.camera} flashMode= {flashMode} type={Camera.Constants.Type.back}
        ref={cameraRef}>
        <View style={styles.buttonContainer}>
          <Svg style={styles.svg}>
          {boundingBoxes.map((box , index) => (
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
            {boundingBoxes.map((box , index) => (
              <Text
              key={`text-${index}`} 
                fontSize="16"
                style={{ color: 'green', paddingTop: box.y, paddingLeft: box.x}}
              >
                {box.class} {'\n'}Distance: {parseFloat(box.distance.toFixed(1))} cm
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
    justifyContent: 'center',
  },
  camera: {
    flex: 1,
  },
  buttonContainer: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: 'transparent',
    margin: 64,
  },
  button: {
    flex: 1,
    alignSelf: 'flex-end',
    alignItems: 'center',
  },
  text: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
});
