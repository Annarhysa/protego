import Link from "next/link";

export default function DashboardLayout({ children }) {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <nav className="bg-white shadow-sm">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            {/* Crime Portal Link */}
            <Link href="/" className="text-xl font-bold text-gray-900 hover:text-gray-700">
              Crime Portal
            </Link>

            {/* Navigation Links */}
            <div className="flex space-x-4">
              {/* Hamburger Menu for Mobile */}
              <div className="md:hidden">
                <button className="text-gray-700 hover:text-gray-900 focus:outline-none">
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M4 6h16M4 12h16m-7 6h7"
                    ></path>
                  </svg>
                </button>
              </div>

              {/* Desktop Navigation Links */}
              <div className="hidden md:flex space-x-4">
                <Link href="/analyze" className="text-gray-700 hover:text-gray-900 font-medium">
                  Analyze Crime Data
                </Link>
                <Link href="/report" className="text-gray-700 hover:text-gray-900 font-medium">
                  Report a Crime
                </Link>
                <Link href="/ask" className="text-gray-700 hover:text-gray-900 font-medium">
                  Query Crime Data
                </Link>
              </div>
            </div>
          </div>

          {/* Mobile Navigation Links (Hidden by Default) */}
          <div className="md:hidden">
            <div className="flex flex-col space-y-2 mt-4">
              <Link href="/analyze" className="text-gray-700 hover:text-gray-900 font-medium">
                Analyze Crime Data
              </Link>
              <Link href="/report" className="text-gray-700 hover:text-gray-900 font-medium">
                Report a Crime
              </Link>
              <Link href="/ask" className="text-gray-700 hover:text-gray-900 font-medium">
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