import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { GlowProjectFooter } from "@/components/TheGlowProject/GlowProjectFooter";
import {
  Heart,
  BookOpen,
  Brain,
  Users,
  FileText,
  Youtube,
  ArrowRight,
  Sparkles,
  Sun,
} from "lucide-react";

export default function TheGlowFoundation() {
  const navigate = useNavigate();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative pt-32 pb-24 px-6">
        <div
          className={`max-w-4xl mx-auto text-center transition-all duration-700 ${
            isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
          }`}
        >
          <div className="inline-flex items-center gap-2 bg-gray-50 px-4 py-2 rounded-full mb-8 border border-gray-100">
            <Sparkles className="w-4 h-4 text-[#e1e65c]" />
            <span className="text-sm font-medium text-gray-700">
              Healing from the inside out
            </span>
          </div>

          <h1 className="text-6xl md:text-7xl font-bold mb-6 leading-tight text-black tracking-tight">
            The Glow Project
          </h1>

          <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed">
            A movement to help people heal emotionally, spiritually, and
            physically — starting with the ARSA community
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center items-center">
            <Button
              size="lg"
              onClick={() => navigate("/glow-process")}
              className="bg-[#e1e65c] text-black hover:bg-[#d4d950] rounded-xl px-8 py-6 text-base font-medium transition-all shadow-sm hover:shadow-md active:scale-95 group"
            >
              Explore The Glow Process
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button
              size="lg"
              onClick={() => navigate("/arsafoundation")}
              className="bg-white text-black hover:bg-gray-50 rounded-xl px-8 py-6 text-base font-medium transition-all border border-gray-200 shadow-sm hover:shadow-md active:scale-95 group"
            >
              Visit ARSA Foundation
              <Heart className="ml-2 w-5 h-5 text-[#d81b1b] group-hover:scale-110 transition-transform" />
            </Button>
          </div>
        </div>
      </section>

      {/* The Duality Section */}
      <section className="py-24 px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-black tracking-tight">
              Two Paths, One Mission
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Helping people find peace, understanding, and connection in body
              and soul
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* The Glow Card */}
            <Card className="group hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-[#e1e65c] bg-white rounded-2xl overflow-hidden cursor-pointer active:scale-[0.98]">
              <CardContent className="p-8">
                <div className="bg-[#e1e65c] w-12 h-12 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <Sun className="w-6 h-6 text-black" />
                </div>
                <h3 className="text-2xl font-bold mb-3 text-black">
                  The Glow Project
                </h3>
                <p className="text-gray-600 mb-6 leading-relaxed text-sm">
                  Emotional, spiritual, and psychological healing through The
                  Glow Process — transforming chaos into clarity, fear into
                  peace.
                </p>
                <ul className="space-y-3 mb-6">
                  <li className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-lg bg-[#e1e65c]/10 flex items-center justify-center flex-shrink-0">
                      <BookOpen className="w-4 h-4 text-[#e1e65c]" />
                    </div>
                    <span className="text-sm text-gray-700">
                      The Glow Book & Philosophy
                    </span>
                  </li>
                  <li className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-lg bg-[#1b86d8]/10 flex items-center justify-center flex-shrink-0">
                      <Brain className="w-4 h-4 text-[#1b86d8]" />
                    </div>
                    <span className="text-sm text-gray-700">
                      GlowGPT AI Assistant
                    </span>
                  </li>
                  <li className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-lg bg-[#e1e65c]/10 flex items-center justify-center flex-shrink-0">
                      <Youtube className="w-4 h-4 text-[#e1e65c]" />
                    </div>
                    <span className="text-sm text-gray-700">
                      YouTube & Courses
                    </span>
                  </li>
                </ul>
                <Button
                  onClick={() => navigate("/glowgpt")}
                  className="w-full bg-black text-white hover:bg-gray-800 rounded-xl py-5 text-sm font-medium transition-all shadow-sm hover:shadow-md active:scale-95 group"
                >
                  Begin Your Journey
                  <Sparkles className="ml-2 w-4 h-4 group-hover:rotate-12 transition-transform" />
                </Button>
              </CardContent>
            </Card>

            {/* ARSA Foundation Card */}
            <Card className="group hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-[#d81b1b] bg-white rounded-2xl overflow-hidden cursor-pointer active:scale-[0.98]">
              <CardContent className="p-8">
                <div className="bg-[#d81b1b] w-12 h-12 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <Heart className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-2xl font-bold mb-3 text-black">
                  ARSA Foundation
                </h3>
                <p className="text-gray-600 mb-6 leading-relaxed text-sm">
                  Physical, medical, and community healing for those with
                  Aberrant Right Subclavian Artery — connecting people to real
                  doctors, real data, and real hope.
                </p>
                <ul className="space-y-3 mb-6">
                  <li className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-lg bg-[#d81b1b]/10 flex items-center justify-center flex-shrink-0">
                      <Users className="w-4 h-4 text-[#d81b1b]" />
                    </div>
                    <span className="text-sm text-gray-700">
                      Support Community
                    </span>
                  </li>
                  <li className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-lg bg-black/10 flex items-center justify-center flex-shrink-0">
                      <FileText className="w-4 h-4 text-black" />
                    </div>
                    <span className="text-sm text-gray-700">
                      Doctor Directory & Resources
                    </span>
                  </li>
                  <li className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-lg bg-[#d81b1b]/10 flex items-center justify-center flex-shrink-0">
                      <Brain className="w-4 h-4 text-[#d81b1b]" />
                    </div>
                    <span className="text-sm text-gray-700">
                      Research & Advocacy
                    </span>
                  </li>
                </ul>
                <Button
                  onClick={() => navigate("/arsafoundation")}
                  className="w-full bg-[#d81b1b] text-white hover:bg-[#c01515] rounded-xl py-5 text-sm font-medium transition-all shadow-sm hover:shadow-md active:scale-95 group"
                >
                  Find Help & Connect
                  <Heart className="ml-2 w-4 h-4 group-hover:scale-110 transition-transform" />
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Featured Content */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-black tracking-tight">
              Start Here
            </h2>
            <p className="text-lg text-gray-600">
              Everything you need to begin your healing journey
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <Card className="hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-gray-300 bg-white rounded-2xl overflow-hidden cursor-pointer active:scale-[0.98]">
              <CardContent className="p-6">
                <div className="bg-[#e1e65c] w-11 h-11 rounded-xl flex items-center justify-center mb-4">
                  <BookOpen className="w-5 h-5 text-black" />
                </div>
                <h3 className="text-lg font-bold mb-2 text-black">
                  The Glow Book
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Read the story that started it all — from chaos to clarity.
                </p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-4 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  Coming Soon
                </Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-gray-300 bg-white rounded-2xl overflow-hidden cursor-pointer active:scale-[0.98]">
              <CardContent className="p-6">
                <div className="bg-[#1b86d8] w-11 h-11 rounded-xl flex items-center justify-center mb-4">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-bold mb-2 text-black">GlowGPT</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Your personal AI guide through The Glow Process.
                </p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-4 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  Join Waitlist
                </Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-gray-300 bg-white rounded-2xl overflow-hidden cursor-pointer active:scale-[0.98]">
              <CardContent className="p-6">
                <div className="bg-black w-11 h-11 rounded-xl flex items-center justify-center mb-4">
                  <Youtube className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-bold mb-2 text-black">
                  YouTube & Courses
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Free content to help you glow every single day.
                </p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-4 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  Watch Now
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Join the Movement */}
      <section className="py-24 px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 text-black tracking-tight">
            You're Not Alone Anymore
          </h2>
          <p className="text-lg text-gray-600 mb-10">
            Join thousands finding healing, hope, and connection through The
            Glow
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button
              size="lg"
              onClick={() => navigate("/arsafoundation")}
              className="bg-black text-white hover:bg-gray-800 rounded-xl px-8 py-6 text-base font-medium transition-all shadow-sm hover:shadow-md active:scale-95"
            >
              Join the Community
            </Button>
            <Button
              size="lg"
              onClick={() => navigate("/about")}
              className="bg-white text-black hover:bg-gray-50 rounded-xl px-8 py-6 text-base font-medium transition-all border border-gray-200 shadow-sm hover:shadow-md active:scale-95"
            >
              Subscribe to Updates
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <GlowProjectFooter />

    </div>
  );
}
