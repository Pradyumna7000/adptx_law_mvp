import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './index.css'

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-adptx-dark-950 text-white flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-4">adptx Legal AI</h1>
            <p className="text-lg mb-8">Something went wrong. Please refresh the page.</p>
            <button 
              onClick={() => window.location.reload()} 
              className="bg-gradient-to-r from-adptx-500 to-adptx-600 hover:from-adptx-600 hover:to-adptx-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-300"
            >
              Refresh Page
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

// Lazy load components with error handling
const LandingPage = React.lazy(() => import('./components/LandingPage'))
const ChatPage = React.lazy(() => import('./components/ChatPage'))

// Fallback component
const FallbackComponent = () => (
  <div className="min-h-screen bg-adptx-dark-950 text-white flex items-center justify-center">
    <div className="text-center">
      <h1 className="text-4xl font-bold mb-4">adptx Legal AI</h1>
      <p className="text-lg mb-8">Loading...</p>
      <div className="flex space-x-2 justify-center">
        <div className="w-2 h-2 bg-adptx-500 rounded-full animate-pulse"></div>
        <div className="w-2 h-2 bg-adptx-500 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
        <div className="w-2 h-2 bg-adptx-500 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
      </div>
    </div>
  </div>
)

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="App">
          <React.Suspense fallback={<FallbackComponent />}>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/chat" element={<ChatPage />} />
            </Routes>
          </React.Suspense>
        </div>
      </Router>
    </ErrorBoundary>
  )
}

export default App 