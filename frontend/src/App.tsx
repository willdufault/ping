import axios from "axios"

export default function App() {
  const API_URL = import.meta.env.VITE_API_URL

  async function handleGetHello(): Promise<void> {
    const response = await axios.get(`${API_URL}/hello`)
    console.log(response.data)
  }

  async function handleGetGoogle(): Promise<void> {
    const response = await axios.get(`${API_URL}/sites`)
    console.log(response.data)
  }

  return (
    <>
      <header className="text-center border-b border-gray-200 bg-gray-100 px-4 py-3 mb-4">
        <h1 className="text-2xl">🛰️ ping</h1>
      </header>
      <main className="max-w-md mx-auto px-4">
        <div className="flex gap-2">
          <button
            className="border border-gray-300 rounded px-3 py-1"
            onClick={handleGetHello}
          >
            get hello
          </button>
          <button
            className="border border-gray-300 rounded px-3 py-1"
            onClick={handleGetGoogle}
          >
            get google
          </button>
        </div>
      </main>
    </>
  )
}
