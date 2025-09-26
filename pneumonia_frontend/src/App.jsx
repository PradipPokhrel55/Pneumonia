import { Route, Routes } from 'react-router-dom'
import Login from "./assets/Page/login.jsx";
import Register from "./assets/Page/register.jsx";
import PneumoniaPredict from "./assets/Page/pneumoniapredict.jsx";
import ProtectedRoute from "./ProtectedRoute.jsx";

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
    </Routes>
  )
}

export default App;
