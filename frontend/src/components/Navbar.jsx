import React from "react";
import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav className="w-full bg-black/60 border-b border-white/10 px-8 py-4 flex justify-between items-center">
      <Link to="/" className="text-2xl font-bold text-white">
        AI Manhwa Generator
      </Link>

      <div className="flex gap-6">
        <Link to="/" className="text-gray-300 hover:text-purple-400">
          Home
        </Link>
        <Link to="/create" className="text-gray-300 hover:text-purple-400">
          Create
        </Link>
        <Link to="/resume" className="text-gray-300 hover:text-purple-400">
          Resume
        </Link>
      </div>
    </nav>
  );
}

export default Navbar;