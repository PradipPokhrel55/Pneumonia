import { Route, Routes } from 'react-router-dom'
import Login from "./assets/Page/login.jsx";
import Register from "./assets/Page/register.jsx";
import PneumoniaPredict from "./assets/Page/pneumoniapredict.jsx";
import ProtectedRoute from "./ProtectedRoute.jsx";
import RAGChat from './assets/Page/RAG.jsx';
import "./index.css"

function App() {
  return (
    <Routes>
      <Route path='/' element={<Login />} />
      <Route path='/register' element={<Register />} />

      <Route path='/predict' element={
        <ProtectedRoute>
          <PneumoniaPredict />
          
        </ProtectedRoute>
      }/>
      <Route path='/chat' element={
        <ProtectedRoute>
          <RAGChat />
          
        </ProtectedRoute>
      }/>
    </Routes>
  )
}

export default App;
