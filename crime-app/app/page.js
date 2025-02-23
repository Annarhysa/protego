import Link from "next/link";

export default function Home() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-8">Welcome to the Crime Portal</h1>
      <div className="space-y-4">
        <Link href="/analyze" className="block text-blue-500 hover:underline">
          Analyze Crime Data
        </Link>
        <Link href="/report" className="block text-blue-500 hover:underline">
          Report a Crime
        </Link>
        <Link href="/query" className="block text-blue-500 hover:underline">
          Query Crime Data
        </Link>
      </div>
    </div>
  );
}