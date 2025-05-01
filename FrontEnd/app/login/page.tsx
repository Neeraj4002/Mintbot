import { Button } from "@/components/ui/button"
import Link from "next/link"

export default function LoginPage() {
  return (
    <div className="min-h-screen flex">
      <div className="w-full md:w-1/2 lg:w-1/3 p-8 flex flex-col justify-center relative z-10">
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-1">character.ai</h1>
        </div>

        <div className="bg-white p-8 rounded-lg shadow-sm">
          <h2 className="text-2xl font-bold text-center mb-2">Get access to</h2>
          <h3 className="text-3xl font-bold text-center mb-4">10M+ Characters</h3>
          <p className="text-center text-gray-600 mb-8">Sign up in just ten seconds</p>

          <div className="space-y-4">
            <Button variant="outline" className="w-full flex items-center justify-center gap-2">
              <svg viewBox="0 0 24 24" width="18" height="18">
                <path
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  fill="#4285F4"
                />
                <path
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  fill="#34A853"
                />
                <path
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  fill="#FBBC05"
                />
                <path
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  fill="#EA4335"
                />
              </svg>
              Continue with Google
            </Button>

            <Button variant="outline" className="w-full flex items-center justify-center gap-2">
              <svg viewBox="0 0 24 24" width="18" height="18">
                <path
                  d="M12 2C6.477 2 2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.879V14.89h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.989C18.343 21.129 22 16.99 22 12c0-5.523-4.477-10-10-10z"
                  fill="#000"
                />
              </svg>
              Continue with Apple
            </Button>

            <div className="relative flex items-center justify-center">
              <div className="border-t border-gray-200 flex-grow"></div>
              <div className="mx-4 text-gray-500 text-sm">OR</div>
              <div className="border-t border-gray-200 flex-grow"></div>
            </div>

            <Button variant="outline" className="w-full">
              Continue with email
            </Button>
          </div>

          <p className="text-xs text-center text-gray-500 mt-6">
            By continuing, you agree with the
            <br />
            <span className="underline">Terms</span> and <span className="underline">Privacy Policy</span>
          </p>
        </div>

        <div className="mt-4 flex justify-between">
          <Link href="/" className="text-sm text-gray-600 hover:underline">
            © 2025 Character.ai
          </Link>
          <div className="flex gap-4">
            <Link href="/" className="text-sm text-gray-600 hover:underline">
              Terms
            </Link>
            <Link href="/" className="text-sm text-gray-600 hover:underline">
              Privacy
            </Link>
          </div>
        </div>
      </div>

      <div className="hidden md:block md:w-1/2 lg:w-2/3 bg-gray-200 relative">
        <img
          src="/placeholder.svg?height=1080&width=1920"
          alt="Character.ai background"
          className="absolute inset-0 w-full h-full object-cover"
        />
      </div>
    </div>
  )
}
