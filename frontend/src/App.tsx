import './App.css'
import {BrowserRouter as Router , Route , Routes } from 'react-router-dom'
import PneumoniaPredict from './assets/PneumoniaPredict'

function App() {

  return (
    <>
    <Router>
      <Routes>
        <Route element={<PneumoniaPredict />} path='/' />
      </Routes>
    </Router>
      
    </>
  )
}

export default App
