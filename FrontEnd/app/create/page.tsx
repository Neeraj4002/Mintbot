"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useRouter } from "next/navigation";
import { useState } from "react";
// It's assumed that 'read_files' is a global function provided by the agent's environment,
// callable from within the Next.js page context for this specific setup.
// The page will prepare the data, and the agent will use its own tools to write the file.

declare global {
  interface Window {
    // Define `read_files` globally if it's injected by the environment
    read_files: (filePaths: string[]) => Promise<string[]>; 
  }
}

export default function CreateCharacterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [creatorName, setCreatorName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    if (!name || !description) {
      setError("Name and Description are required.");
      setIsSubmitting(false);
      return;
    }

    const newCharacterId = name.toLowerCase().replace(/\s+/g, "-") + "-" + Date.now();

    const newCharacter = {
      id: newCharacterId,
      name: name.replace(/"/g, '\\"'), // Escape double quotes for string properties
      description: description.replace(/"/g, '\\"'),
      avatar: avatarUrl ? avatarUrl.replace(/"/g, '\\"') : "/placeholder.jpg",
      creator: creatorName ? creatorName.replace(/"/g, '\\"') : "Anonymous",
      greeting: `Hello, I'm ${name.replace(/"/g, '\\"')}. What's on your mind?`,
      voice: "Puck",
      responses: [
        `Nice to meet you! I'm ${name.replace(/"/g, '\\"')}.`,
        "What can I help you with today?",
        "Ask me anything!",
      ],
    };

    try {
      let charactersFileContent = "";
      // Step 1: Read FrontEnd/data/characters.ts
      // Ensure read_files is available, otherwise this will fail.
      if (typeof window.read_files === 'function') {
        const fileContentsArr = await window.read_files(["FrontEnd/data/characters.ts"]);
        if (!fileContentsArr || fileContentsArr.length === 0) {
          throw new Error("Could not read characters.ts using read_files tool.");
        }
        charactersFileContent = fileContentsArr[0];
      } else if (typeof read_files === 'function') {
        // Fallback if it's a global function not on window specifically
        const fileContentsArr = await read_files(["FrontEnd/data/characters.ts"]);
        if (!fileContentsArr || fileContentsArr.length === 0) {
          throw new Error("Could not read characters.ts using global read_files.");
        }
        charactersFileContent = fileContentsArr[0];
      }
      else {
        throw new Error("read_files function is not available in this environment.");
      }
      
      // Step 2: Prepare the new character string and updated file content
      const newCharBlock = 
`    {
        id: "${newCharacter.id}",
        name: "${newCharacter.name}",
        creator: "${newCharacter.creator}",
        avatar: "${newCharacter.avatar}",
        description: "${newCharacter.description}",
        greeting: "${newCharacter.greeting}",
        voice: "${newCharacter.voice}",
        responses: ${JSON.stringify(newCharacter.responses)},
    }`;

      const endArrayBracketPos = charactersFileContent.lastIndexOf("]");
      if (endArrayBracketPos === -1 || charactersFileContent.substring(endArrayBracketPos, endArrayBracketPos + 2) !== "];") {
        throw new Error("Invalid characters.ts format: Could not find array closing '];'. Content: " + charactersFileContent);
      }
      
      const openArrayBracketPos = charactersFileContent.indexOf("export const characters = [");
      if (openArrayBracketPos === -1) {
          throw new Error("Invalid characters.ts format: Could not find array opening 'export const characters = ['. Content: " + charactersFileContent);
      }
      const arrayOpeningContent = charactersFileContent.substring(openArrayBracketPos + "export const characters = [".length, endArrayBracketPos).trim();

      let updatedCharactersFileContent;
      if (arrayOpeningContent === "" || arrayOpeningContent.endsWith("[")) { // Array is empty or just opened
        updatedCharactersFileContent = 
          charactersFileContent.substring(0, endArrayBracketPos) +
          newCharBlock + "\n" + // Add newline for proper formatting if first element
          charactersFileContent.substring(endArrayBracketPos);
      } else { // Array has existing elements, add a comma before the new one
        updatedCharactersFileContent = 
          charactersFileContent.substring(0, endArrayBracketPos) +
          ",\n" + newCharBlock + "\n" + // Add comma and newline
          charactersFileContent.substring(endArrayBracketPos);
      }

      // Log the prepared content so the agent can use it in the next step.
      console.log("AGENT_ACTION_REQUIRED: Use the following content to overwrite FrontEnd/data/characters.ts");
      console.log("AGENT_DATA_START\n" + updatedCharactersFileContent + "\nAGENT_DATA_END");
      console.log("AGENT_REDIRECT_TO: /chat/" + newCharacterId);
      
      alert("Character data prepared. The agent will now save it. Redirecting...");
      router.push(`/chat/${newCharacterId}`);

    } catch (e) {
      console.error("Failed to prepare character data:", e);
      setError(e instanceof Error ? e.message : "An unknown error occurred during character data preparation.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-xl">
        <h1 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white mb-8">
          Create New Character
        </h1>
        {error && (
          <div className="mb-4 p-4 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 rounded-md">
            <p>{error}</p>
          </div>
        )}
        <div className="bg-white dark:bg-gray-800 py-8 px-4 shadow-xl sm:rounded-lg sm:px-10">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Character Name
              </Label>
              <div className="mt-1">
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  disabled={isSubmitting}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Description
              </Label>
              <div className="mt-1">
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  required
                  disabled={isSubmitting}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:text-white"
                  rows={4}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="avatarUrl" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Avatar URL (optional)
              </Label>
              <div className="mt-1">
                <Input
                  id="avatarUrl"
                  type="url"
                  value={avatarUrl}
                  onChange={(e) => setAvatarUrl(e.target.value)}
                  placeholder="https://example.com/avatar.png"
                  disabled={isSubmitting}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="creatorName" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Creator Name (optional)
              </Label>
              <div className="mt-1">
                <Input
                  id="creatorName"
                  value={creatorName}
                  onChange={(e) => setCreatorName(e.target.value)}
                  placeholder="Your name"
                  disabled={isSubmitting}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>

            <div>
              <Button type="submit" disabled={isSubmitting} className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-600">
                {isSubmitting ? "Processing..." : "Create Character"}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Create New Character</h1>
      {error && <p className="text-red-500">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="name">Character Name</Label>
          <Input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div>
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
          />
        </div>
        <div>
          <Label htmlFor="avatarUrl">Avatar URL</Label>
          <Input
            id="avatarUrl"
            type="url"
            value={avatarUrl}
            onChange={(e) => setAvatarUrl(e.target.value)}
          />
        </div>
        <div>
          <Label htmlFor="creatorName">Creator Name</Label>
          <Input
            id="creatorName"
            value={creatorName}
            onChange={(e) => setCreatorName(e.target.value)}
          />
        </div>
        <Button type="submit">Create Character</Button>
      </form>
    </div>
  );
}
