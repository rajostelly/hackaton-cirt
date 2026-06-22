export function LoadingSpinner() {
  return (
    <div className="flex justify-center items-center py-12">
      <div className="w-8 h-8 border-2 border-gray-700 border-t-white rounded-full animate-spin" />
    </div>
  );
}
