import React from 'react'
import { Link } from 'react-router-dom'

const FallbackComponent = () => {
  return (
    <div className="min-h-screen bg-adptx-dark-950 text-white flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">adptx Legal AI</h1>
        <p className="text-lg mb-8">India's AI Legal Research Assistant</p>
        <div className="space-y-4">
          <Link 
            to="/chat" 
            className="inline-block bg-gradient-to-r from-adptx-500 to-adptx-600 hover:from-adptx-600 hover:to-adptx-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-300 mr-4"
          >
            Try the Tool
          </Link>
          <Link 
            to="/test-chat" 
            className="inline-block bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-300"
          >
            Test Chat
          </Link>
        </div>
      </div>
    </div>
  )
}

export default FallbackComponent 