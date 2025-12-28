import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from "react-native";
import { useNavigation } from "@react-navigation/native";

const RAGChat = () => {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const navigation = useNavigation();

  const handleAsk = async () => {
    if (!query.trim()) return;

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/rag-query/?query=${encodeURIComponent(
          query
        )}`
      );
      const data = await res.json();
      setAnswer(data.answer);
      setQuery("");
    } catch (err) {
      console.error(err);
      Alert.alert("Error", "Failed to fetch answer.");
    }
  };

  const handleLogout = () => {
    // Remove auth token logic
    // localStorage equivalent in React Native could be AsyncStorage
    // But for demo, simple alert:
    Alert.alert("Logout", "You have been logged out.");
    navigation.navigate("Login"); // Assuming a Login screen exists
  };

  const handlePredictNavigate = () => {
    navigation.navigate("Predict"); // Navigate to PneumoniaPredict screen
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      style={styles.container}
    >
      {/* Top buttons */}
      <View style={styles.topButtons}>
        <TouchableOpacity
          style={[styles.topButton, { backgroundColor: "#16a34a" }]}
          onPress={handlePredictNavigate}
        >
          <Text style={styles.buttonText}>Predict</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.topButton, { backgroundColor: "#dc2626" }]}
          onPress={handleLogout}
        >
          <Text style={styles.buttonText}>Logout</Text>
        </TouchableOpacity>
      </View>

      {/* Answer Box */}
      <ScrollView style={styles.scrollArea} contentContainerStyle={{ flexGrow: 1 }}>
        {answer ? (
          <View style={styles.answerBox}>
            <Text style={styles.answerTitle}>Answer:</Text>
            <Text style={styles.answerText}>{answer}</Text>
          </View>
        ) : (
          <Text style={styles.placeholderText}>Your answers will appear here.</Text>
        )}
      </ScrollView>

      {/* Input Area */}
      <View style={styles.inputArea}>
        <TextInput
          style={styles.input}
          placeholder="Type your question..."
          value={query}
          onChangeText={setQuery}
        />
        <TouchableOpacity style={styles.askButton} onPress={handleAsk}>
          <Text style={styles.askButtonText}>Ask</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

export default RAGChat;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#e0f2fe",
    paddingTop: 50,
  },
  topButtons: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingHorizontal: 20,
    marginBottom: 10,
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
  scrollArea: {
    flex: 1,
    paddingHorizontal: 20,
    marginBottom: 10,
  },
  answerBox: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#d1d5db",
    marginBottom: 10,
  },
  answerTitle: {
    fontWeight: "bold",
    fontSize: 16,
    marginBottom: 4,
    color: "#1e3a8a",
  },
  answerText: {
    fontSize: 16,
    color: "#1f2937",
  },
  placeholderText: {
    textAlign: "center",
    color: "#9ca3af",
    marginTop: 20,
  },
  inputArea: {
    flexDirection: "row",
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderTopWidth: 1,
    borderColor: "#d1d5db",
    backgroundColor: "#fff",
    alignItems: "center",
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: "#9ca3af",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginRight: 10,
  },
  askButton: {
    backgroundColor: "#2563eb",
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  askButtonText: {
    color: "#fff",
    fontWeight: "bold",
  },
});
