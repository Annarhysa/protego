import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center py-12">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Welcome to the Crime Portal
        </h1>
        <p className="text-xl text-gray-600">
          Your one-stop solution for crime analysis, reporting, and querying.
        </p>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 w-full max-w-6xl px-4">
        {/* Analyze Crime Data */}
        <Link href="/analyze">
          <div className="bg-white p-8 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 cursor-pointer text-center h-full flex flex-col justify-between">
            <div className="text-4xl text-blue-500 mb-4">📊</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Analyze Crime Data
            </h2>
            <p className="text-gray-600">
              Explore and analyze crime statistics with advanced tools.
            </p>
          </div>
        </Link>

        {/* Report a Crime */}
        <Link href="/report">
          <div className="bg-white p-8 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 cursor-pointer text-center h-full flex flex-col justify-between">
            <div className="text-4xl text-blue-500 mb-4">🚨</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Report a Crime
            </h2>
            <p className="text-gray-600">
              Report a crime quickly and securely.
            </p>
          </div>
        </Link>

        {/* Query Crime Data */}
        <Link href="/ask">
          <div className="bg-white p-8 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 cursor-pointer text-center h-full flex flex-col justify-between">
            <div className="text-4xl text-blue-500 mb-4">🔍</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Query Crime Data
            </h2>
            <p className="text-gray-600">
              Get detailed information about specific crimes.
            </p>
          </div>
        </Link>

        {/* Additional Card Example */}
        {/* <Link href="/example">
          <div className="bg-white p-8 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 cursor-pointer text-center h-full flex flex-col justify-between">
            <div className="text-4xl text-blue-500 mb-4">📋</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Example Feature
            </h2>
            <p className="text-gray-600">
              This is an example of an additional feature card.
            </p>
          </div>
        </Link> */}
      </div>
    </div>
  );
}