import React, { useState, useContext } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  Image,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from "react-native";
import * as ImagePicker from "react-native-image-picker";
import axios from "axios";
import AuthContext from "../Auth/AuthContext";
import { useNavigation } from "@react-navigation/native";

const PneumoniaPredict = () => {
  const [imageUri, setImageUri] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const { authTokens, logoutUser } = useContext(AuthContext);
  const navigation = useNavigation();

  const pickImage = () => {
    ImagePicker.launchImageLibrary(
      { mediaType: "photo", quality: 0.7 },
      (response) => {
        if (response.didCancel) {
          console.log("User cancelled image picker");
        } else if (response.errorCode) {
          console.log("ImagePicker Error: ", response.errorMessage);
        } else if (response.assets && response.assets.length > 0) {
          setImageUri(response.assets[0].uri);
          setPrediction(null);
        }
      }
    );
  };

  const handleSubmit = async () => {
    if (!imageUri) {
      Alert.alert("Error", "Please select an image first.");
      return;
    }

    if (!authTokens || !authTokens.access) {
      Alert.alert("Error", "Authentication failed. Please log in again.");
      return;
    }

    const formData = new FormData();
    formData.append("file", {
      uri: imageUri,
      type: "image/jpeg",
      name: "pneumonia.jpg",
    });

    try {
      setLoading(true);
      const response = await axios.post(
        "http://localhost:8000/api/predict/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${authTokens.access}`,
          },
        }
      );
      setPrediction(response.data);
    } catch (err) {
      console.error(err);
      Alert.alert(
        "Error",
        err.response?.data?.detail || "Something went wrong."
      );
      setPrediction(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      {/* Top Buttons */}
      <View style={styles.topButtons}>
        <TouchableOpacity
          onPress={() => navigation.navigate("Chat")}
          style={[styles.topButton, { backgroundColor: "#16a34a" }]}
        >
          <Text style={styles.buttonText}>Chat</Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={logoutUser}
          style={[styles.topButton, { backgroundColor: "#dc2626" }]}
        >
          <Text style={styles.buttonText}>Logout</Text>
        </TouchableOpacity>
      </View>

      {/* Picker */}
      <TouchableOpacity style={styles.picker} onPress={pickImage}>
        <Text style={styles.pickerText}>
          {imageUri ? "Change Image" : "Select Image"}
        </Text>
      </TouchableOpacity>

      {imageUri && (
        <Image source={{ uri: imageUri }} style={styles.imagePreview} />
      )}

      {/* Predict Button */}
      <TouchableOpacity
        onPress={handleSubmit}
        style={styles.predictButton}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.predictButtonText}>Predict</Text>
        )}
      </TouchableOpacity>

      {/* Prediction Result */}
      {prediction && (
        <View style={styles.resultBox}>
          <Text style={styles.resultText}>
            Prediction: {prediction.prediction}
          </Text>
          <Text style={styles.resultText}>
            Confidence: {(prediction.confidence * 100).toFixed(2)}%
          </Text>
        </View>
      )}
    </View>
  );
};

export default PneumoniaPredict;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#e0f2fe",
    alignItems: "center",
    padding: 20,
    paddingTop: 60,
  },
  topButtons: {
    flexDirection: "row",
    justifyContent: "space-between",
    width: "100%",
    marginBottom: 20,
  },
  topButton: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  buttonText: {
    color: "#fff",
    fontWeight: "bold",
  },
  picker: {
    backgroundColor: "#3b82f6",
    padding: 12,
    borderRadius: 8,
    marginBottom: 20,
  },
  pickerText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 16,
  },
  imagePreview: {
    width: 250,
    height: 250,
    borderRadius: 12,
    marginBottom: 20,
  },
  predictButton: {
    backgroundColor: "#2563eb",
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    marginBottom: 20,
  },
  predictButtonText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 16,
  },
  resultBox: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 10,
    width: "100%",
    alignItems: "center",
  },
  resultText: {
    fontSize: 16,
    fontWeight: "500",
    marginVertical: 4,
  },
});
