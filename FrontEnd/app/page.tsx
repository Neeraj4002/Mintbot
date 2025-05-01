import { Sidebar } from "@/components/sidebar"
import { CharacterGrid } from "@/components/character-grid"

export default function Home() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-6 md:p-10">
        <div className="max-w-5xl mx-auto">
          <h1 className="text-4xl font-bold mb-2">What do you want to do?</h1>
          <p className="text-xl text-gray-600 mb-12">Rule with power. Scheme with style.</p>

          <h2 className="text-2xl font-semibold mb-6">Featured</h2>
          <CharacterGrid />
        </div>
      </main>
    </div>
  )
}
