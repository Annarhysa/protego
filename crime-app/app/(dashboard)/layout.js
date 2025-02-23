import Link from "next/link";

export default function DashboardLayout({ children }) {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <nav className="bg-white shadow-sm">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-bold text-gray-900">Crime Portal</h1>
            <div className="flex space-x-4">
              <Link href="/analyze" className="text-gray-700 hover:text-gray-900 font-medium">
                Analyze Crime Data
              </Link>
              <Link href="/report" className="text-gray-700 hover:text-gray-900 font-medium">
                Report a Crime
              </Link>
              <Link href="/query" className="text-gray-700 hover:text-gray-900 font-medium">
                Query Crime Data
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Centered Content */}
      <div className="flex-1 flex items-center justify-center bg-gray-50 py-12">
        <div className="w-full max-w-4xl px-4">
          {children}
        </div>
      </div>
    </div>
  );
}