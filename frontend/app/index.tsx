export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Todo App</h1>
        <p className="text-gray-600">Welcome to the Todo application!</p>
        <div className="mt-6">
          <a 
            href="/login" 
            className="mr-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md"
          >
            Login
          </a>
          <a 
            href="/signup" 
            className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-md"
          >
            Sign Up
          </a>
        </div>
      </div>
    </div>
  );
}