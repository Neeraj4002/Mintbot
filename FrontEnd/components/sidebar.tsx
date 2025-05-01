"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Search, Home } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { characters } from "@/data/characters"

export function Sidebar() {
  const [searchQuery, setSearchQuery] = useState("")
  const pathname = usePathname()

  const isActive = (path: string) => {
    return pathname === path
  }

  return (
    <aside className="w-64 border-r h-screen flex flex-col bg-white">
      <div className="p-4 border-b">
        <h1 className="text-xl font-bold mb-4">Persona.ai</h1>
        <Link href="/create">
          <Button className="w-full flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Create
          </Button>
        </Link>
      </div>

      <nav className="p-2">
        <Link href="/">
          <Button variant={isActive("/") ? "secondary" : "ghost"} className="w-full justify-start mb-1">
            <Home className="h-4 w-4 mr-2" />
            Discover
          </Button>
        </Link>
      </nav>

      <div className="p-4">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search for Characters"
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {pathname.startsWith("/chat") && (
        <div className="p-2">
          <h2 className="text-sm font-medium text-gray-500 px-2 mb-2">Today</h2>
          <div className="space-y-1">
            {characters.map((character) => (
              <Link key={character.id} href={`/chat/${character.id}`}>
                <Button
                  variant={pathname === `/chat/${character.id}` ? "secondary" : "ghost"}
                  className="w-full justify-start"
                >
                  <div className="w-6 h-6 rounded-full overflow-hidden mr-2">
                    <img
                      src={character.avatar || "/placeholder.svg"}
                      alt={character.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <span className="truncate">{character.name}</span>
                </Button>
              </Link>
            ))}
          </div>
        </div>
      )}

      <div className="mt-auto p-4 text-xs text-gray-500 flex items-center justify-between">
        <Link href="/privacy" className="hover:underline">
          Privacy Policy
        </Link>
        <span>•</span>
        <Link href="/terms" className="hover:underline">
          Terms of Service
        </Link>
      </div>

      <div className="p-4 border-t">
        <Link href="/upgrade">
          <Button variant="outline" className="w-full">
            Upgrade to p.ai+
          </Button>
        </Link>
      </div>
    </aside>
  )
}
