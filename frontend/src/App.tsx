import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { TutorProvider } from './context/TutorContext'
import { TutorPanel } from './components/TutorPanel'
import { ArchGallery } from './pages/ArchGallery'
import { ArchMode } from './pages/ArchMode'
import { ExamMode } from './pages/ExamMode'
import { Home } from './pages/Home'
import { ReviewMode } from './pages/ReviewMode'
import { SettingsMode } from './pages/SettingsMode'
import { StatsMode } from './pages/StatsMode'
import { StudyMode } from './pages/StudyMode'
import './index.css'

export default function App() {
  return (
    <TutorProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/exam" element={<ExamMode />} />
          <Route path="/study" element={<StudyMode />} />
          <Route path="/review" element={<ReviewMode />} />
          <Route path="/stats" element={<StatsMode />} />
          <Route path="/settings" element={<SettingsMode />} />
          <Route path="/arch" element={<ArchMode />} />
          <Route path="/arch/gallery" element={<ArchGallery />} />
        </Routes>
        <TutorPanel />
      </BrowserRouter>
    </TutorProvider>
  )
}
