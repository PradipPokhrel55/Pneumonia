import React, { useState, useContext } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheer } from "react-native";
import { useNavigation } from "@react-navigation/native";
import AuthContext from "../Auth/AuthContext";

const LoginPage = () => {
  const { loginUser } = useContext(AuthContext);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigation = useNavigation();

  const handleSubmit = async () => {
    await loginUser(username, password);
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity
        onPress={() => navigation.navigate("Register")}
        style={styles.registerLink}
      >
        <Text style={styles.registerText}>Register</Text>
      </TouchableOpacity>

      <View style={styles.form}>
        <Text style={styles.title}>Login</Text>

        <TextInput
          value={username}
          onChangeText={setUsername}
          placeholder="Enter username"
          style={styles.input}
        />
        <TextInput
          value={password}
          onChangeText={setPassword}
          placeholder="Enter password"
          secureTextEntry
          style={styles.input}
        />

        <TouchableOpacity onPress={handleSubmit} style={styles.button}>
          <Text style={styles.buttonText}>Login</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#f3f4f6",
    padding: 16,
  },
  registerLink: {
    position: "absolute",
    top: 16,
    right: 16,
  },
  registerText: {
    color: "#3b82f6",
    textDecorationLine: "underline",
  },
  form: {
    width: "100%",
    maxWidth: 400,
    backgroundColor: "#ffffff",
    padding: 24,
    borderRadius: 8,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 5,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#1f2937",
    marginBottom: 16,
  },
  input: {
    width: "100%",
    padding: 12,
    borderColor: "#d1d5db",
    borderWidth: 1,
    borderRadius: 4,
    marginBottom: 12,
  },
  button: {
    width: "100%",
    backgroundColor: "#3b82f6",
    padding: 12,
    borderRadius: 4,
    alignItems: "center",
  },
  buttonText: {
    color: "#ffffff",
    fontWeight: "bold",
  },
});

export default LoginPage;