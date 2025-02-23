export default function DashboardLayout({ children }) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-8">Crime Awareness and Reporting Portal</h1>
        {children}
      </div>
    );
  }