import React from 'react'
import { Link } from 'react-router-dom'
import { Search, FileText, Scale, ArrowRight, Menu, X, CheckCircle, Shield, TrendingUp, Zap, Users, BarChart3 } from 'lucide-react'

const LandingPage = () => {
  const [isMenuOpen, setIsMenuOpen] = React.useState(false)

  const features = [
    {
      icon: <Search className="w-8 h-8 text-adptx-500" />,
      title: "Advanced Legal Research",
      description: "Comprehensive legal research with AI-powered analysis, case law retrieval, and argument simulation."
    },
    {
      icon: <FileText className="w-8 h-8 text-blue-500" />,
      title: "Document Analysis",
      description: "Analyze legal documents, contracts, and agreements with risk assessment and compliance checking."
    },
    {
      icon: <Shield className="w-8 h-8 text-purple-500" />,
      title: "Contract Review",
      description: "Specialized contract analysis with legal implications, risk mitigation, and strategic recommendations."
    },
    {
      icon: <Scale className="w-8 h-8 text-adptx-orange-500" />,
      title: "Argument Simulation",
      description: "Generate strong legal arguments, counterarguments, and rebuttal strategies using AI."
    },
    {
      icon: <TrendingUp className="w-8 h-8 text-green-500" />,
      title: "Predictive Analytics",
      description: "AI-powered predictions for case outcomes, success probabilities, and legal strategy optimization."
    },
    {
      icon: <Zap className="w-8 h-8 text-yellow-500" />,
      title: "Real-time Processing",
      description: "Lightning-fast legal analysis with comprehensive monitoring and quality assurance."
    }
  ]

  const benefits = [
    "All-in-one legal research tool",
    "Save 80% of manual research time",
    "Access to comprehensive Indian legal database",
    "AI-powered legal document analysis",
    "Real-time case law updates",
    "Professional-grade legal insights"
  ]

  return (
    <div className="min-h-screen bg-adptx-dark-950">
      {/* Navigation */}
              <nav className="fixed top-0 w-full bg-adptx-dark-900/80 backdrop-blur-md border-b border-adptx-dark-800 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
                              <img src="/logo_without_bg.png" alt="ADPTX" className="h-8 w-auto" />
              <span className="ml-2 text-xl font-bold gradient-text">ADPTX</span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#home" className="text-gray-300 hover:text-white transition-colors">Home</a>
              <a href="#features" className="text-gray-300 hover:text-white transition-colors">Features</a>
              <a href="#about" className="text-gray-300 hover:text-white transition-colors">About</a>
              <Link to="/chat" className="btn-primary">Try the Tool</Link>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="text-gray-300 hover:text-white"
              >
                {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {isMenuOpen && (
            <div className="md:hidden">
              <div className="px-2 pt-2 pb-3 space-y-1">
                <a href="#home" className="block px-3 py-2 text-gray-300 hover:text-white">Home</a>
                <a href="#features" className="block px-3 py-2 text-gray-300 hover:text-white">Features</a>
                <a href="#about" className="block px-3 py-2 text-gray-300 hover:text-white">About</a>
                <Link to="/chat" className="block px-3 py-2 btn-primary text-center">Try the Tool</Link>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section id="home" className="hero-gradient pt-24 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-8">
              India's AI Legal Research Assistant
            </h1>
            <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-4xl mx-auto leading-relaxed">
              Built for Lawyers. Reduces research time from hours to minutes.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/chat" className="btn-primary text-lg px-8 py-4">
                Start Researching Now
                <ArrowRight className="ml-2 inline-block w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-adptx-dark-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Advanced Legal AI Features
            </h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Comprehensive legal research and analysis powered by advanced AI with multi-agent coordination
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="card group hover:scale-105 transition-transform duration-300">
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Enhanced Capabilities Section */}
              <section className="py-20 bg-adptx-dark-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                Enhanced AI Capabilities
              </h2>
              <p className="text-xl text-gray-400 mb-8">
                Advanced features that set adptx apart from traditional legal research tools
              </p>
              
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                              <div className="w-8 h-8 bg-adptx-500/20 rounded-full flex items-center justify-center flex-shrink-0">
              <Zap className="w-4 h-4 text-adptx-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg mb-2">Multi-Agent Coordination</h3>
                    <p className="text-gray-400">Specialized AI agents work together for comprehensive legal analysis</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                    <Shield className="w-4 h-4 text-blue-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg mb-2">Quality Control & Validation</h3>
                    <p className="text-gray-400">Advanced error handling, retry logic, and quality scoring</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                    <BarChart3 className="w-4 h-4 text-purple-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg mb-2">Performance Monitoring</h3>
                    <p className="text-gray-400">Real-time statistics, execution tracking, and quality metrics</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                    <Users className="w-4 h-4 text-green-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg mb-2">Document Analysis</h3>
                    <p className="text-gray-400">Contract review, risk assessment, and compliance checking</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="relative">
              <div className="bg-adptx-dark-800 rounded-xl p-6 border border-adptx-dark-700">
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-sm text-gray-300">AI Legal Research Active</span>
                  </div>
                  <div className="space-y-2">
                    <div className="h-2 bg-adptx-dark-700 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-adptx-500 to-adptx-600 rounded-full animate-pulse" style={{width: '75%'}}></div>
                    </div>
                    <div className="text-xs text-gray-400">Processing legal query...</div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2 text-sm">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span className="text-gray-300">Law retrieval completed</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span className="text-gray-300">Case research completed</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm">
                      <div className="w-4 h-4 border-2 border-adptx-500 border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-gray-300">Generating arguments...</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Why adptx Section */}
      <section id="about" className="py-20 bg-adptx-dark-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Why Choose <span className="gradient-text">adptx</span>?
            </h2>
            <p className="text-xl text-gray-400 mb-8 max-w-3xl mx-auto">
              Transform your legal research workflow with AI-powered insights and comprehensive Indian legal database access.
            </p>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-4xl mx-auto">
              {benefits.map((benefit, index) => (
                <div key={index} className="flex items-center space-x-3 text-left">
                  <CheckCircle className="w-5 h-5 text-adptx-500 flex-shrink-0" />
                  <span className="text-gray-300">{benefit}</span>
                </div>
              ))}
            </div>
            <div className="mt-8">
              <Link to="/chat" className="btn-secondary">
                Try adptx Now
                <ArrowRight className="ml-2 inline-block w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-adptx-dark-900 border-t border-adptx-dark-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <img src="/logo_without_bg.png" alt="adptx" className="h-8 w-auto" />
                <span className="ml-2 text-xl font-bold gradient-text">adptx</span>
              </div>
              <p className="text-gray-400 mb-4">
                Advanced AI-powered legal research and analysis platform for Indian lawyers.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold text-lg mb-4">Features</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Legal Research</li>
                <li>Document Analysis</li>
                <li>Contract Review</li>
                <li>Risk Assessment</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-lg mb-4">Resources</h3>
              <ul className="space-y-2 text-gray-400">
                <li>API Documentation</li>
                <li>Legal Database</li>
                <li>Case Studies</li>
                <li>Support</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-lg mb-4">Contact</h3>
              <ul className="space-y-2 text-gray-400">
                <li>adptx.solutions@gmail.com</li>
                <li>+91 99011 55126</li>
                <li>Bengaluru, India</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-adptx-dark-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 adptx. All rights reserved. Advanced Legal AI Research Platform.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage 