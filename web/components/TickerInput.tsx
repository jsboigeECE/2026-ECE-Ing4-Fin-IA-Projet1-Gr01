"use client";

import { useState, useEffect, useRef } from "react";

interface TickerInputProps {
    onSearch: (ticker: string) => void;
    isLoading: boolean;
}

interface SearchResult {
    symbol: string;
    name: string;
}

export default function TickerInput({ onSearch, isLoading }: TickerInputProps) {
    const [ticker, setTicker] = useState("AAPL");
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<SearchResult[]>([]);
    const [showResults, setShowResults] = useState(false);
    const searchRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
                setShowResults(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleSearch = async (val: string) => {
        if (!val || val.length < 2) {
            setResults([]);
            return;
        }

        try {
            const res = await fetch(`http://localhost:8000/search?q=${val}`);
            if (res.ok) {
                const data = await res.json();
                setResults(data);
                setShowResults(true);
            }
        } catch (e) {
            console.error(e);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = e.target.value;
        setTicker(val.toUpperCase());
        handleSearch(val);
    };

    const handleSelect = (symbol: string) => {
        setTicker(symbol);
        setShowResults(false);
        onSearch(symbol);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (ticker.trim()) {
            onSearch(ticker.trim());
            setShowResults(false);
        }
    };

    return (
        <div className="relative w-full max-w-md" ref={searchRef}>
            <form onSubmit={handleSubmit} className="flex gap-2">
                <div className="relative flex-grow">
                    <input
                        type="text"
                        value={ticker}
                        onChange={handleChange}
                        placeholder="Search Asset (e.g., Apple, Air Liquide...)"
                        className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 uppercase font-mono text-black"
                        disabled={isLoading}
                        onFocus={() => { if (results.length > 0) setShowResults(true); }}
                    />
                    {/* Dropdown */}
                    {showResults && results.length > 0 && (
                        <div className="absolute z-50 w-full bg-white mt-1 border border-gray-200 rounded-lg shadow-xl max-h-60 overflow-y-auto">
                            {results.map((r, idx) => (
                                <div
                                    key={idx}
                                    className="px-4 py-2 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-0"
                                    onClick={() => handleSelect(r.symbol)}
                                >
                                    <div className="font-bold text-gray-900">{r.symbol}</div>
                                    <div className="text-xs text-gray-500 truncate">{r.name}</div>
                                </div>
                            ))}
                        </div>
                    )}

                    {showResults && results.length === 0 && ticker.length > 2 && (
                        <div className="absolute z-50 w-full bg-white mt-1 border border-gray-200 rounded-lg shadow-xl p-4 text-center text-gray-400 text-sm">
                            No local assets found matching "{ticker}".
                        </div>
                    )}

                </div>
                <button
                    type="submit"
                    disabled={isLoading}
                    className="px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors whitespace-nowrap"
                >
                    {isLoading ? "Analyzing..." : "Analyze"}
                </button>
            </form>
        </div>
    );
}
