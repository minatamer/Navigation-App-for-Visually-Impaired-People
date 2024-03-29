import React, { useState , useEffect} from 'react'
import { View, Text, StyleSheet, Button, FlatList } from 'react-native'
import { FAB } from 'react-native-paper'


export default function Home(props) {   
    useEffect(() => {
        console.log('Welcome to the Navigation Assisting App!');
        return () =>{};
      }, []);
    
    return (
        <View style = {{flex:1}}>
            <FAB
                style ={styles.fab}
                icon="camera"
                backgroundColor = "#ffffff"
                onPress = {()=> props.navigation.navigate('Detect')}
            />
        </View>
  )
}


const styles = StyleSheet.create({
    cardStyle: {
        padding: 10,
        margin: 10,
    },
    

    fab: {
        position: "absolute",
        margin: 16,
        right: 0,
        bottom: 0,
    }
})