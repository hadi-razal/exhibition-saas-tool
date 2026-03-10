import { Button } from "@/components/ui/button";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "Pricing — ExhibitIQ",
    description: "Choose the right plan for your exhibition intelligence needs.",
};

const plans = [
    {
        name: "Starter",
        price: "$29",
        period: "/month",
        description: "Perfect for small teams exploring exhibition data extraction.",
        features: [
            "5 floor plan uploads / month",
            "50 exhibitor scrapes / month",
            "CSV & JSON export",
            "Basic OCR extraction",
            "Email support",
        ],
        cta: "Get Started",
        popular: false,
        color: "primary",
    },
    {
        name: "Pro",
        price: "$79",
        period: "/month",
        description: "For agencies and teams that need full extraction power.",
        features: [
            "50 floor plan uploads / month",
            "500 exhibitor scrapes / month",
            "CSV, Excel & JSON export",
            "Advanced OCR + pattern matching",
            "Detail page traversal",
            "LinkedIn & contact extraction",
            "Priority support",
        ],
        cta: "Start Pro Trial",
        popular: true,
        color: "primary",
    },
    {
        name: "Agency",
        price: "$199",
        period: "/month",
        description: "Unlimited power for enterprise exhibition intelligence.",
        features: [
            "Unlimited floor plan uploads",
            "Unlimited exhibitor scrapes",
            "All export formats",
            "Full OCR + AI extraction",
            "Auto-pagination & detail pages",
            "Bulk processing",
            "API access",
            "Dedicated support",
            "Custom integrations",
        ],
        cta: "Contact Sales",
        popular: false,
        color: "chart-2",
    },
];

export default function PricingPage() {
    return (
        <div className="py-24">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="text-center mb-16">
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-primary/20 bg-primary/5 text-sm text-primary mb-6">
                        Pricing
                    </div>
                    <h1 className="text-4xl sm:text-5xl font-bold mb-4">
                        Simple, Transparent{" "}
                        <span className="gradient-text">Pricing</span>
                    </h1>
                    <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                        Choose the plan that fits your exhibition intelligence needs.
                        All plans include access to both extraction tools.
                    </p>
                </div>

                {/* Plans */}
                <div className="grid md:grid-cols-3 gap-6 lg:gap-8 max-w-6xl mx-auto">
                    {plans.map((plan) => (
                        <div
                            key={plan.name}
                            className={`relative rounded-2xl p-8 transition-all duration-300 ${plan.popular
                                    ? "glass-card border-primary/30 shadow-lg shadow-primary/10 scale-105"
                                    : "glass-card hover:border-primary/20"
                                }`}
                        >
                            {plan.popular && (
                                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                                    <span className="px-4 py-1 rounded-full bg-primary text-primary-foreground text-xs font-semibold shadow-lg shadow-primary/30">
                                        Most Popular
                                    </span>
                                </div>
                            )}

                            <div className="mb-6">
                                <h3 className="text-lg font-semibold mb-2">{plan.name}</h3>
                                <p className="text-sm text-muted-foreground mb-4">{plan.description}</p>
                                <div className="flex items-baseline gap-1">
                                    <span className="text-4xl font-bold">{plan.price}</span>
                                    <span className="text-muted-foreground text-sm">{plan.period}</span>
                                </div>
                            </div>

                            <ul className="space-y-3 mb-8">
                                {plan.features.map((feature) => (
                                    <li key={feature} className="flex items-start gap-3 text-sm">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="text-primary mt-0.5 flex-shrink-0">
                                            <polyline points="20 6 9 17 4 12" />
                                        </svg>
                                        <span className="text-muted-foreground">{feature}</span>
                                    </li>
                                ))}
                            </ul>

                            <Button
                                className={`w-full ${plan.popular
                                        ? "bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/25"
                                        : "bg-card hover:bg-accent border border-border/60"
                                    }`}
                            >
                                {plan.cta}
                            </Button>
                        </div>
                    ))}
                </div>

                {/* Bottom note */}
                <div className="mt-16 text-center">
                    <p className="text-sm text-muted-foreground">
                        Pricing is displayed for illustration purposes. This is a local MVP — all features are accessible now.
                    </p>
                    <Link href="/dashboard" className="inline-block mt-4">
                        <Button variant="outline" className="border-primary/30 hover:bg-primary/10 text-primary">
                            Open the App for Free →
                        </Button>
                    </Link>
                </div>
            </div>
        </div>
    );
}
