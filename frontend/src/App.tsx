import { ChakraProvider } from '@chakra-ui/react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ChakraProvider>
        <Router>
          <Routes>
            <Route path="/" element={<div>Welcome to Tempo</div>} />
          </Routes>
        </Router>
      </ChakraProvider>
    </QueryClientProvider>
  )
}

export default App 