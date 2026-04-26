"use client";

import Link from "next/link";
import dynamic from "next/dynamic";
import { useState } from "react";
import AuthGuard from "../components/AuthGuard";

const Map = dynamic(() => import("../components/Map"), {
  ssr: false,
});

type Hotel = {
  name: string;
  price: string;
};

type DayPlan = {
  date: string;
  activities: string[];
  hotels: Hotel[];
  restaurants: string[];
};

type Itinerary = {
  summary: string;
  days: DayPlan[];
};

const fallbackCatalog: Record<
  string,
  {
    hotels: Hotel[];
    restaurants: string[];
  }
> = {
  low: {
    hotels: [
      { name: "Backpacker Nest", price: "Rs. 1,200/night" },
      { name: "City Budget Inn", price: "Rs. 1,800/night" },
    ],
    restaurants: ["Local Tiffin House", "Street Spice Corner"],
  },
  medium: {
    hotels: [
      { name: "Comfort Stay Suites", price: "Rs. 3,500/night" },
      { name: "Harbor View Hotel", price: "Rs. 4,200/night" },
    ],
    restaurants: ["Coastal Kitchen", "The Market Table"],
  },
  high: {
    hotels: [
      { name: "Grand Horizon Resort", price: "Rs. 8,500/night" },
      { name: "Lotus Premium Retreat", price: "Rs. 10,000/night" },
    ],
    restaurants: ["Saffron Deck", "Skyline Fine Dining"],
  },
};

function normalizeBudget(value: string) {
  const lower = value.trim().toLowerCase();

  if (
    lower.includes("low") ||
    lower.includes("budget") ||
    lower.includes("cheap")
  ) {
    return "low";
  }

  if (
    lower.includes("high") ||
    lower.includes("luxury") ||
    lower.includes("premium")
  ) {
    return "high";
  }

  const amount = Number.parseInt(lower.replace(/[^\d]/g, ""), 10);

  if (!Number.isNaN(amount)) {
    if (amount < 5000) return "low";
    if (amount > 15000) return "high";
  }

  return "medium";
}

function buildFallbackItinerary(
  destination: string,
  days: number,
  budget: string
): Itinerary {
  const tier = normalizeBudget(budget);
  const catalog = fallbackCatalog[tier];
  const safeDestination = destination || "your destination";

  return {
    summary: `${days}-day plan for ${safeDestination} with ${tier} budget recommendations.`,
    days: Array.from({ length: days }, (_, index) => ({
      date: `Day ${index + 1}`,
      activities: [
        `Explore the best local spots in ${safeDestination}`,
        "Try one signature attraction during the afternoon",
        "Keep the evening open for food and photos",
      ],
      hotels: catalog.hotels,
      restaurants: catalog.restaurants,
    })),
  };
}

function parseLegacyItinerary(
  rawText: string,
  destination: string,
  days: number,
  budget: string
): Itinerary {
  const fallback = buildFallbackItinerary(destination, days, budget);
  const activityLines = rawText
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => /^Day\s+\d+:/i.test(line));

  if (!activityLines.length) {
    return fallback;
  }

  return {
    summary: fallback.summary,
    days: activityLines.map((line, index) => ({
      date: `Day ${index + 1}`,
      activities: [line.replace(/^Day\s+\d+:\s*/i, "")],
      hotels: fallback.days[index % fallback.days.length].hotels,
      restaurants: fallback.days[index % fallback.days.length].restaurants,
    })),
  };
}

function normalizeResponse(
  data: unknown,
  destination: string,
  days: number,
  budget: string
): Itinerary {
  const payload = data as
    | {
        summary?: string;
        days?: DayPlan[];
        itinerary?: string;
      }
    | undefined;

  if (payload?.days?.length) {
    return {
      summary:
        payload.summary ||
        `${days}-day plan for ${destination || "your destination"}.`,
      days: payload.days,
    };
  }

  if (payload?.itinerary) {
    return parseLegacyItinerary(payload.itinerary, destination, days, budget);
  }

  return buildFallbackItinerary(destination, days, budget);
}

export default function Planner() {
  const [destination, setDestination] = useState("");
  const [days, setDays] = useState("3");
  const [budget, setBudget] = useState("medium");
  const [selectedItem, setSelectedItem] = useState<Hotel | null>(null);
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generatePlan = async () => {
    const tripDays = Number.parseInt(days, 10) || 3;

    setLoading(true);
    setError("");
    setSelectedItem(null);

    try {
      const res = await fetch("http://127.0.0.1:5000/generate_itinerary", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          destination,
          days: tripDays,
          budget,
        }),
      });

      if (!res.ok) {
        throw new Error("Planner service unavailable");
      }

      const data = await res.json();
      setItinerary(normalizeResponse(data, destination, tripDays, budget));
    } catch {
      setItinerary(buildFallbackItinerary(destination, tripDays, budget));
      setError(
        "Backend response was unavailable, so fallback recommendations are shown."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthGuard>
      <main className="app-shell">
        <section className="planner-header">
          <div>
            <p className="eyebrow">Trip planner</p>
            <h1 className="section-title">Plan your trip with budget-based picks</h1>
          </div>
          <div className="nav-links">
            <Link href="/">Home</Link>
            <Link href="/profile">Profile</Link>
          </div>
        </section>

        <section className="planner-layout">
          <div className="form-card">
            <h2>Trip details</h2>

            <label className="field-label" htmlFor="destination">
              Destination
            </label>
            <input
              id="destination"
              className="input-field"
              placeholder="Goa, Jaipur, Manali..."
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
            />

            <label className="field-label" htmlFor="days">
              Days
            </label>
            <input
              id="days"
              className="input-field"
              type="number"
              min="1"
              value={days}
              onChange={(e) => setDays(e.target.value)}
            />

            <label className="field-label" htmlFor="budget">
              Budget
            </label>
            <select
              id="budget"
              className="input-field"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>

            <button className="primary-button" onClick={generatePlan} disabled={loading}>
              {loading ? "Generating..." : "Generate itinerary"}
            </button>

            {error ? <p className="inline-note">{error}</p> : null}
          </div>

          <div className="results-panel">
            <div className="map-frame">
              <Map location={destination || "Goa"} />
            </div>

            {itinerary ? (
              <>
                <div className="results-header">
                  <h2>Your travel plan</h2>
                  <p>{itinerary.summary}</p>
                </div>

                <div className="results-grid">
                  {itinerary.days.map((day) => (
                    <article key={day.date} className="day-card">
                      <h3>{day.date}</h3>

                      <div className="card-section">
                        <h4>Activities</h4>
                        <ul className="bullet-list">
                          {day.activities.map((activity) => (
                            <li key={activity}>{activity}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="card-section">
                        <h4>Hotels</h4>
                        <ul className="bullet-list">
                          {day.hotels.map((hotel) => (
                            <li key={`${day.date}-${hotel.name}`}>
                              <button
                                className="list-link"
                                onClick={() => setSelectedItem(hotel)}
                              >
                                {hotel.name} - {hotel.price}
                              </button>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div className="card-section">
                        <h4>Restaurants</h4>
                        <ul className="bullet-list">
                          {day.restaurants.map((restaurant) => (
                            <li key={`${day.date}-${restaurant}`}>{restaurant}</li>
                          ))}
                        </ul>
                      </div>
                    </article>
                  ))}
                </div>
              </>
            ) : (
              <div className="empty-state">
                <h2>Your itinerary will appear here</h2>
                <p>
                  Choose a destination, number of days, and budget to generate a
                  trip plan with stay and food suggestions.
                </p>
              </div>
            )}
          </div>
        </section>

        {selectedItem ? (
          <aside className="details-drawer">
            <h2>Stay details</h2>
            <p>
              <strong>Hotel:</strong> {selectedItem.name}
            </p>
            <p>
              <strong>Price:</strong> {selectedItem.price}
            </p>
            <p>
              <strong>Destination:</strong> {destination || "Selected trip"}
            </p>
            <button className="secondary-button" onClick={() => setSelectedItem(null)}>
              Close
            </button>
          </aside>
        ) : null}
      </main>
    </AuthGuard>
  );
}
