import Link from "next/link"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { characters } from "@/data/characters"

export function CharacterGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {characters.map((character) => (
        <Link key={character.id} href={`/chat/${character.id}`}>
          <Card className="h-full hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="aspect-square rounded-full overflow-hidden mx-auto mb-4 w-32 h-32">
                <img
                  src={character.avatar || "/placeholder.svg"}
                  alt={character.name}
                  className="w-full h-full object-cover"
                />
              </div>
              <h3 className="text-xl font-semibold text-center">{character.name}</h3>
              <p className="text-sm text-gray-500 text-center">By {character.creator}</p>
            </CardContent>
            <CardFooter className="p-4 pt-0 text-sm text-center text-gray-600">{character.description}</CardFooter>
          </Card>
        </Link>
      ))}
    </div>
  )
}
