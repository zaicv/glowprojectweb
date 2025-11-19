import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Sun, Moon, Heart, ArrowRight, Sparkles, Menu, X, Eye, Wind, Brain, Zap, Shield, BookOpen, Users, CheckCircle2, Quote } from 'lucide-react';

export default function PhilosophyPage() {
  const [scrollY, setScrollY] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const [mobileMenu, setMobileMenu] = useState(false);
  const [activePhase, setActivePhase] = useState(0);

  useEffect(() => {
    setIsVisible(true);
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const timelineEvents = [
    { year: "Age 17", title: "The Diagnosis", desc: "ARSA discovered — a rare vascular anomaly threatening every breath and swallow" },
    { year: "2 Surgeries", title: "Medical Survival", desc: "Body saved, but nervous system left in perpetual fear" },
    { year: "Years of Chaos", title: "Living in Fear", desc: "Anxiety, withdrawal, perfectionism — unable to trust my own body" },
    { year: "The Discovery", title: "Finding The Glow", desc: "Beneath all the noise, a quiet awareness that never left" },
    { year: "The Framework", title: "Building the Process", desc: "Systematizing survival alchemy into a replicable path" },
    { year: "The Movement", title: "The Glow Project", desc: "So no one else has to face this alone" }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-xl z-50 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#e1e65c] flex items-center justify-center">
              <Sun className="w-5 h-5 text-black" />
            </div>
            <span className="text-xl font-semibold text-black">The Glow Project</span>
          </div>
          
          <div className="hidden md:flex items-center gap-1">
            <button className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-black hover:bg-gray-50 rounded-lg transition-all">Philosophy</button>
            <button className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-black hover:bg-gray-50 rounded-lg transition-all">The Process</button>
            <button className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-black hover:bg-gray-50 rounded-lg transition-all">GlowGPT</button>
            <button className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-black hover:bg-gray-50 rounded-lg transition-all">Community</button>
          </div>

          <div className="flex items-center gap-3">
            <Button className="bg-black text-white hover:bg-gray-800 rounded-xl px-5 py-2 text-sm font-medium transition-all shadow-sm hover:shadow-md">
              Start Your Journey
            </Button>
            <button className="md:hidden p-2 hover:bg-gray-50 rounded-lg transition-all" onClick={() => setMobileMenu(!mobileMenu)}>
              {mobileMenu ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {mobileMenu && (
          <div className="md:hidden border-t border-gray-100 bg-white">
            <div className="px-6 py-4 space-y-1">
              <button className="w-full text-left px-4 py-3 text-sm font-medium text-gray-700 hover:text-black hover:bg-gray-50 rounded-lg transition-all">Philosophy</button>
              <button className="w-full text-left px-4 py-3 text-sm font-medium text-gray-700 hover:text-black hover:bg-gray-50 rounded-lg transition-all">The Process</button>
              <button className="w-full text-left px-4 py-3 text-sm font-medium text-gray-700 hover:text-black hover:bg-gray-50 rounded-lg transition-all">GlowGPT</button>
              <button className="w-full text-left px-4 py-3 text-sm font-medium text-gray-700 hover:text-black hover:bg-gray-50 rounded-lg transition-all">Community</button>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-24 px-6 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#e1e65c]/5 to-transparent pointer-events-none" />
        <div className={`max-w-5xl mx-auto text-center relative transition-all duration-700 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <div className="inline-flex items-center gap-2 bg-white px-4 py-2 rounded-full mb-8 border border-gray-200 shadow-sm">
            <Sparkles className="w-4 h-4 text-[#e1e65c]" />
            <span className="text-sm font-medium text-gray-700">The story behind the movement</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight text-black tracking-tight">
            This Isn't Theory.<br />This Is Survival.
          </h1>
          
          <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed">
            The Glow Project was born from a life that nearly ended at 17 — and the decade-long journey to remember what it means to be alive beyond fear.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center items-center">
            <Button size="lg" className="bg-[#e1e65c] text-black hover:bg-[#d4d950] rounded-xl px-8 py-6 text-base font-medium transition-all shadow-sm hover:shadow-md active:scale-95 group">
              <Heart className="mr-2 w-5 h-5" />
              Read Isaiah's Story
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button size="lg" className="bg-white text-black hover:bg-gray-50 rounded-xl px-8 py-6 text-base font-medium transition-all border border-gray-200 shadow-sm hover:shadow-md active:scale-95">
              Watch the Origin Video
            </Button>
          </div>
        </div>
      </section>

      {/* The Origin Story */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="mb-16">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-1 h-12 bg-[#e1e65c] rounded-full" />
              <h2 className="text-4xl md:text-5xl font-bold text-black tracking-tight">Where It Began</h2>
            </div>
            <p className="text-lg text-gray-600 leading-relaxed">
              Isaiah Briggs' story doesn't start with wellness — it starts with a rare medical condition that nearly took his life.
            </p>
          </div>

          <div className="space-y-8">
            <Card className="border border-gray-200 bg-gradient-to-br from-gray-50 to-white rounded-2xl">
              <CardContent className="p-8">
                <div className="flex items-start gap-6">
                  <div className="w-14 h-14 rounded-xl bg-[#d81b1b]/10 flex items-center justify-center flex-shrink-0">
                    <Heart className="w-7 h-7 text-[#d81b1b]" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold mb-4 text-black">The Diagnosis: ARSA</h3>
                    <p className="text-gray-700 leading-relaxed mb-4">
                      At 17, Isaiah was diagnosed with <span className="font-semibold text-black">Aberrant Right Subclavian Artery (ARSA)</span> — a rare vascular anomaly where an artery wraps around the esophagus, compressing it like a silent hand.
                    </p>
                    <p className="text-gray-700 leading-relaxed mb-4">
                      Every swallow became fear. Every breath carried an echo of danger. Two major surgeries saved his life, but surviving wasn't the same as living.
                    </p>
                    <div className="bg-[#d81b1b]/5 rounded-xl p-4 border border-[#d81b1b]/20">
                      <p className="text-sm text-gray-700 italic">
                        "The medical world fixed my anatomy, but no one taught me how to trust my body again."
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 bg-gradient-to-br from-gray-50 to-white rounded-2xl">
              <CardContent className="p-8">
                <div className="flex items-start gap-6">
                  <div className="w-14 h-14 rounded-xl bg-black/10 flex items-center justify-center flex-shrink-0">
                    <Moon className="w-7 h-7 text-black" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold mb-4 text-black">Years in Chaos</h3>
                    <p className="text-gray-700 leading-relaxed mb-4">
                      The aftermath wasn't just physical. Chronic fatigue, anxiety, and a nervous system stuck in survival mode. Isaiah withdrew from life — overthinking, overcontrolling, unable to trust the very body that had once betrayed him.
                    </p>
                    <p className="text-gray-700 leading-relaxed mb-4">
                      What he didn't know then was that this internal noise had a name: <span className="font-semibold text-black">Chaos</span>.
                    </p>
                    <div className="space-y-2">
                      <div className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-black flex-shrink-0 mt-2" />
                        <span className="text-sm text-gray-700">Perfectionism to avoid failure</span>
                      </div>
                      <div className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-black flex-shrink-0 mt-2" />
                        <span className="text-sm text-gray-700">Anxiety about every physical sensation</span>
                      </div>
                      <div className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-black flex-shrink-0 mt-2" />
                        <span className="text-sm text-gray-700">Belief that he had to earn safety through control</span>
                      </div>
                      <div className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-black flex-shrink-0 mt-2" />
                        <span className="text-sm text-gray-700">Disconnection from joy, presence, and self</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-2 border-[#e1e65c] bg-gradient-to-br from-[#e1e65c]/5 to-white rounded-2xl">
              <CardContent className="p-8">
                <div className="flex items-start gap-6">
                  <div className="w-14 h-14 rounded-xl bg-[#e1e65c] flex items-center justify-center flex-shrink-0">
                    <Sun className="w-7 h-7 text-black" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold mb-4 text-black">The Discovery of The Glow</h3>
                    <p className="text-gray-700 leading-relaxed mb-4">
                      Somewhere in those years of collapse and rebuilding, Isaiah began to notice something beneath all the noise — a quiet, radiant presence that fear couldn't touch.
                    </p>
                    <p className="text-gray-700 leading-relaxed mb-4">
                      It wasn't something he found. It was something he <span className="font-semibold text-black">remembered</span>.
                    </p>
                    <div className="bg-[#e1e65c]/10 rounded-xl p-6 border border-[#e1e65c]/20">
                      <Quote className="w-8 h-8 text-[#e1e65c] mb-4" />
                      <p className="text-lg text-gray-800 italic leading-relaxed mb-2">
                        "The Glow is the quiet pulse of existence — not something you find, but something you remember."
                      </p>
                      <p className="text-sm text-gray-600">— The essence of The Glow</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Timeline */}
      <section className="py-24 px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-black tracking-tight">The Journey from Chaos to Glow</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              A timeline of survival, discovery, and the birth of a movement
            </p>
          </div>

          <div className="relative">
            {/* Timeline Line */}
            <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-black via-[#e1e65c] to-[#e1e65c] hidden md:block" />
            
            <div className="space-y-8">
              {timelineEvents.map((event, index) => (
                <div key={index} className="relative pl-0 md:pl-24">
                  {/* Timeline Dot */}
                  <div className="absolute left-6 top-6 w-5 h-5 rounded-full bg-white border-4 border-[#e1e65c] hidden md:block" />
                  
                  <Card className="border border-gray-200 hover:border-[#e1e65c] bg-white rounded-2xl hover:shadow-lg transition-all">
                    <CardContent className="p-6">
                      <div className="flex items-start gap-4">
                        <div className="bg-[#e1e65c]/10 px-3 py-1 rounded-lg flex-shrink-0">
                          <span className="text-sm font-bold text-black">{event.year}</span>
                        </div>
                        <div className="flex-1">
                          <h3 className="text-xl font-bold text-black mb-2">{event.title}</h3>
                          <p className="text-gray-700">{event.desc}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* The Dual Force Model */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-black tracking-tight">Understanding the Two Forces</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Every human experience exists in the dialogue between Chaos and The Glow
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-12">
            {/* Chaos */}
            <Card className="group border border-gray-200 hover:border-black bg-gradient-to-br from-gray-50 to-white rounded-2xl overflow-hidden hover:shadow-xl transition-all duration-300">
              <CardContent className="p-8">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-14 h-14 rounded-xl bg-black flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Moon className="w-7 h-7 text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-black">Chaos</h3>
                    <p className="text-sm text-gray-500">The survival mind on autopilot</p>
                  </div>
                </div>
                
                <p className="text-gray-700 leading-relaxed mb-6">
                  Chaos is the egoic trance — the unconscious identification with thought, fear, and survival patterns. It's the voice that says "you're not safe" and "you're not enough." It arose to protect you, but now it keeps you small.
                </p>

                <div className="space-y-3 mb-6">
                  <div className="bg-gray-100 rounded-lg p-3">
                    <p className="text-sm font-medium text-black mb-1">What it sounds like:</p>
                    <p className="text-sm text-gray-700 italic">"I have to be perfect or I don't matter"</p>
                  </div>
                  <div className="bg-gray-100 rounded-lg p-3">
                    <p className="text-sm font-medium text-black mb-1">What it feels like:</p>
                    <p className="text-sm text-gray-700">Racing thoughts, tight chest, shallow breath, urgency</p>
                  </div>
                  <div className="bg-gray-100 rounded-lg p-3">
                    <p className="text-sm font-medium text-black mb-1">What it creates:</p>
                    <p className="text-sm text-gray-700">Anxiety, overthinking, perfectionism, disconnection</p>
                  </div>
                </div>

                <div className="bg-black/5 rounded-xl p-4 border border-black/10">
                  <p className="text-sm text-gray-700">
                    <span className="font-semibold text-black">The truth:</span> Chaos isn't evil. It's a frightened system trying to help. But it's no longer in charge.
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* The Glow */}
            <Card className="group border-2 border-[#e1e65c] hover:border-[#d4d950] bg-gradient-to-br from-[#e1e65c]/5 to-white rounded-2xl overflow-hidden hover:shadow-xl transition-all duration-300">
              <CardContent className="p-8">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-14 h-14 rounded-xl bg-[#e1e65c] flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Sun className="w-7 h-7 text-black" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-black">The Glow</h3>
                    <p className="text-sm text-gray-500">Pure awareness, existence itself</p>
                  </div>
                </div>
                
                <p className="text-gray-700 leading-relaxed mb-6">
                  The Glow is the silent awareness beneath all thought — the space you return to when you exhale fully. It's not something to chase or earn. It's what remains when you stop identifying with the noise. It's life before story.
                </p>

                <div className="space-y-3 mb-6">
                  <div className="bg-[#e1e65c]/10 rounded-lg p-3 border border-[#e1e65c]/20">
                    <p className="text-sm font-medium text-black mb-1">What it sounds like:</p>
                    <p className="text-sm text-gray-700 italic">"I am here. I am safe. I am enough."</p>
                  </div>
                  <div className="bg-[#e1e65c]/10 rounded-lg p-3 border border-[#e1e65c]/20">
                    <p className="text-sm font-medium text-black mb-1">What it feels like:</p>
                    <p className="text-sm text-gray-700">Open chest, calm breath, spaciousness, peace</p>
                  </div>
                  <div className="bg-[#e1e65c]/10 rounded-lg p-3 border border-[#e1e65c]/20">
                    <p className="text-sm font-medium text-black mb-1">What it creates:</p>
                    <p className="text-sm text-gray-700">Clarity, presence, compassion, authentic connection</p>
                  </div>
                </div>

                <div className="bg-[#e1e65c]/10 rounded-xl p-4 border border-[#e1e65c]/20">
                  <p className="text-sm text-gray-700">
                    <span className="font-semibold text-black">The truth:</span> The Glow was never gone. You just forgot how to feel it. This is the remembrance.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* The Shift */}
          <Card className="border-2 border-[#e1e65c] bg-gradient-to-br from-[#e1e65c]/10 via-white to-white rounded-3xl">
            <CardContent className="p-12 text-center">
              <div className="w-16 h-16 rounded-2xl bg-black flex items-center justify-center mx-auto mb-6">
                <Zap className="w-8 h-8 text-[#e1e65c]" />
              </div>
              <h3 className="text-3xl font-bold text-black mb-4">The Shift</h3>
              <p className="text-xl text-gray-700 leading-relaxed max-w-2xl mx-auto mb-4">
                You are not Chaos. You are the awareness that sees it.
              </p>
              <p className="text-gray-600 max-w-xl mx-auto">
                The Glow Process teaches you to recognize Chaos, disidentify from it, and return to presence — over and over, until it becomes your new default.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* The Manifesto */}
      <section className="py-24 px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-black tracking-tight">The Manifesto</h2>
            <p className="text-lg text-gray-600">
              What The Glow Project stands for
            </p>
          </div>

          <Card className="border border-gray-200 bg-white rounded-3xl mb-12">
            <CardContent className="p-12">
              <div className="space-y-8">
                <div className="text-center pb-8 border-b border-gray-200">
                  <Quote className="w-12 h-12 text-[#e1e65c] mx-auto mb-6" />
                  <p className="text-2xl font-semibold text-black leading-relaxed mb-4">
                    "The Glow is not something you chase.<br />It's something you remember."
                  </p>
                  <p className="text-gray-600">
                    This is a movement rooted in truth, not trends. In depth, not dopamine. In freedom, not fear.
                  </p>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-bold text-black mb-4">What We Believe</h3>
                    <div className="space-y-3">
                      <div className="flex items-start gap-3">
                        <CheckCircle2 className="w-5 h-5 text-[#e1e65c] flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700">Authenticity over appearance</span>
                      </div>
                      <div className="flex items-start gap-3">
                        <CheckCircle2 className="w-5 h-5 text-[#e1e65c] flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700">Transparency over performance</span>
                      </div>
                      <div className="flex items-start gap-3">
                        <CheckCircle2 className="w-5 h-5 text-[#e1e65c] flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700">Compassion with strength</span>
                      </div>
                      <div className="flex items-start gap-3">
                        <CheckCircle2 className="w-5 h-5 text-[#e1e65c] flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700">Science and soul, united</span>
                      </div>
                      <div className="flex items-start gap-3">
                        <CheckCircle2 className="w-5 h-5 text-[#e1e65c] flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700">Integrity over profit</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-bold text-black mb-4">What We Reject</h3>
                    <div className="space-y-3">
                      <div className="flex items-start gap-3">
                        <div className="w-5 h-5 rounded-full bg-black flex items-center justify-center flex-shrink-0 mt-0.5">
                          <X className="w-3 h-3 text-white" />
                        </div>
                        <span className="text-sm text-gray-700">Toxic perfectionism and hustle culture</span>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-5 h-5 rounded-full bg-black flex items-center justify-center flex-shrink-0 mt-0.5">
                          <X className="w-3 h-3 text-white" />
                        </div>
                        <span className="text-sm text-gray-700">Performative "wellness" without depth</span>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-5 h-5 rounded-full bg-black flex items-center justify-center flex-shrink-0 mt-0.5">
                          <X className="w-3 h-3 text-white" />
                        </div>
                        <span className="text-sm text-gray-700">Exploiting pain for profit</span>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-5 h-5 rounded-full bg-black flex items-center justify-center flex-shrink-0 mt-0.5">
                          <X className="w-3 h-3 text-white" />
                        </div>
                        <span className="text-sm text-gray-700">Spiritual bypassing and false calm</span>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-5 h-5 rounded-full bg-black flex items-center justify-center flex-shrink-0 mt-0.5">
                          <X className="w-3 h-3 text-white" />
                        </div>
                        <span className="text-sm text-gray-700">One-size-fits-all "solutions"</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="bg-gradient-to-br from-[#e1e65c]/10 to-white rounded-2xl p-8 border border-[#e1e65c]/20 text-center">
            <h3 className="text-2xl font-bold text-black mb-4">The Spirit of The Glow</h3>
            <p className="text-gray-700 leading-relaxed max-w-2xl mx-auto">
              The Glow is not about being perfect — it's about being <span className="font-semibold text-black">real</span>. It's grounded, intelligent, driven — yet guided by softness and awareness, not ego or pride. We reject toxic competitiveness and embrace conscious creation: clarity without control, power without domination, ambition without chaos.
            </p>
          </div>
        </div>
      </section>

      {/* What Sets Us Apart */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-black tracking-tight">What Makes Us Different</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              This isn't another wellness brand — it's a lived philosophy backed by science and soul
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <Card className="border border-gray-200 hover:border-[#70ac85] bg-white rounded-2xl hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="bg-[#70ac85]/10 w-12 h-12 rounded-xl flex items-center justify-center mb-6">
                  <Heart className="w-6 h-6 text-[#70ac85]" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-black">It's Human, Not Clinical</h3>
                <p className="text-sm text-gray-700 leading-relaxed">
                  Rooted in trauma-informed psychology and neuroscience, yet spoken in language that touches the heart. No jargon, no distance — just truth.
                </p>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 hover:border-[#e1e65c] bg-white rounded-2xl hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="bg-[#e1e65c]/10 w-12 h-12 rounded-xl flex items-center justify-center mb-6">
                  <Shield className="w-6 h-6 text-[#e1e65c]" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-black">Not Performative Healing</h3>
                <p className="text-sm text-gray-700 leading-relaxed">
                  No filters, no fake calm. This is real nervous system regulation and embodied truth — not aesthetic wellness for social media.
                </p>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 hover:border-[#1b86d8] bg-white rounded-2xl hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="bg-[#1b86d8]/10 w-12 h-12 rounded-xl flex items-center justify-center mb-6">
                  <Brain className="w-6 h-6 text-[#1b86d8]" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-black">Integrative by Design</h3>
                <p className="text-sm text-gray-700 leading-relaxed">
                  The Glow lives across every portal — book, app, community, foundation — all unified by one mission: help you remember who you are.
                </p>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 hover:border-black bg-white rounded-2xl hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="bg-black/10 w-12 h-12 rounded-xl flex items-center justify-center mb-6">
                  <Users className="w-6 h-6 text-black" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-black">A Movement, Not a Company</h3>
                <p className="text-sm text-gray-700 leading-relaxed">
                  Every decision is filtered through empathy and integrity. We vow to never exploit pain for profit or hide behind corporate distance.
                </p>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 hover:border-[#70ac85] bg-white rounded-2xl hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="bg-[#70ac85]/10 w-12 h-12 rounded-xl flex items-center justify-center mb-6">
                  <Eye className="w-6 h-6 text-[#70ac85]" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-black">Built From Experience</h3>
                <p className="text-sm text-gray-700 leading-relaxed">
                  Isaiah lived this. Every framework, every tool, every word comes from a decade of survival alchemy — not theory.
                </p>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 hover:border-[#e1e65c] bg-white rounded-2xl hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="bg-[#e1e65c]/10 w-12 h-12 rounded-xl flex items-center justify-center mb-6">
                  <BookOpen className="w-6 h-6 text-[#e1e65c]" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-black">Science Meets Soul</h3>
                <p className="text-sm text-gray-700 leading-relaxed">
                  We bridge neuroplasticity, somatic therapy, and consciousness — refusing to choose between evidence and experience.
                </p>
              </CardContent>
            </Card>
          </div>

          <Card className="border-2 border-[#e1e65c] bg-gradient-to-br from-[#e1e65c]/5 to-white rounded-2xl">
            <CardContent className="p-8 text-center">
              <h3 className="text-2xl font-bold text-black mb-4">The Promise</h3>
              <p className="text-lg text-gray-700 leading-relaxed max-w-2xl mx-auto">
                The Glow Project exists so no one has to go through what Isaiah did — <span className="font-semibold text-black">isolated, misunderstood, and afraid</span>. It exists to prove that even in the deepest chaos, there's light waiting underneath — not to be chased, but remembered.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* The Ecosystem */}
      <section className="py-24 px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-black tracking-tight">How The Glow Lives</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Every portal is an entry point to the same truth
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="border border-gray-200 hover:border-[#e1e65c] bg-white rounded-2xl hover:shadow-lg transition-all cursor-pointer active:scale-[0.98]">
              <CardContent className="p-6 text-center">
                <div className="bg-[#e1e65c] w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <BookOpen className="w-6 h-6 text-black" />
                </div>
                <h3 className="font-bold text-black mb-2">The Book</h3>
                <p className="text-sm text-gray-600 mb-4">The philosophy and story — where it all began</p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-3 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  Coming Soon
                </Button>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 hover:border-[#70ac85] bg-white rounded-2xl hover:shadow-lg transition-all cursor-pointer active:scale-[0.98]">
              <CardContent className="p-6 text-center">
                <div className="bg-[#70ac85] w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-bold text-black mb-2">GlowGPT</h3>
                <p className="text-sm text-gray-600 mb-4">Your AI guide through the Process</p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-3 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  Try Beta
                </Button>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 hover:border-[#d81b1b] bg-white rounded-2xl hover:shadow-lg transition-all cursor-pointer active:scale-[0.98]">
              <CardContent className="p-6 text-center">
                <div className="bg-[#d81b1b] w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <Heart className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-bold text-black mb-2">ARSA Foundation</h3>
                <p className="text-sm text-gray-600 mb-4">Medical support and community</p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-3 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  Learn More
                </Button>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 hover:border-black bg-white rounded-2xl hover:shadow-lg transition-all cursor-pointer active:scale-[0.98]">
              <CardContent className="p-6 text-center">
                <div className="bg-black w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <Users className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-bold text-black mb-2">Community</h3>
                <p className="text-sm text-gray-600 mb-4">Connect with others on the path</p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-3 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  Join Discord
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Why It Matters */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <Card className="border-2 border-black bg-gradient-to-br from-gray-50 to-white rounded-3xl overflow-hidden">
            <CardContent className="p-12">
              <div className="text-center mb-8">
                <div className="w-16 h-16 rounded-2xl bg-black flex items-center justify-center mx-auto mb-6">
                  <Sun className="w-8 h-8 text-[#e1e65c]" />
                </div>
                <h2 className="text-3xl md:text-4xl font-bold mb-6 text-black tracking-tight">
                  Why The Glow Matters
                </h2>
              </div>

              <div className="space-y-6 mb-8">
                <p className="text-lg text-gray-700 leading-relaxed">
                  Isaiah's journey from nearly losing his life at 17 to rebuilding it from the ground up is the blueprint for The Glow Project's mission — to show that <span className="font-semibold text-black">healing isn't about becoming something new, but returning to what's always been true.</span>
                </p>
                <p className="text-lg text-gray-700 leading-relaxed">
                  Too many people are told their anxiety is "just in their head." Too many are given medication but not meaning. Too many are surviving but not living.
                </p>
                <p className="text-lg text-gray-700 leading-relaxed">
                  The Glow Project bridges the gap between medical intervention and soul restoration. It meets you where you are — in the chaos — and shows you the way back to peace.
                </p>
              </div>

              <div className="bg-[#e1e65c]/10 rounded-2xl p-6 border border-[#e1e65c]/20 mb-8">
                <Quote className="w-8 h-8 text-[#e1e65c] mb-4" />
                <p className="text-xl text-gray-800 italic leading-relaxed mb-4">
                  "You are not broken. You were never broken. You just forgot who you were beneath the fear."
                </p>
                <p className="text-sm text-gray-600">— The heart of The Glow</p>
              </div>

              <div className="text-center">
                <p className="text-gray-700 mb-6">
                  If you're ready to remember, we're here to guide you home.
                </p>
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <Button size="lg" className="bg-[#e1e65c] text-black hover:bg-[#d4d950] rounded-xl px-8 py-6 text-base font-medium transition-all shadow-sm hover:shadow-md active:scale-95">
                    Start Your Journey
                  </Button>
                  <Button size="lg" className="bg-white text-black hover:bg-gray-50 rounded-xl px-8 py-6 text-base font-medium transition-all border border-gray-200 shadow-sm hover:shadow-md active:scale-95">
                    Join Community
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-12 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-[#e1e65c] flex items-center justify-center">
                  <Sun className="w-4 h-4 text-black" />
                </div>
                <span className="font-semibold text-black">The Glow Project</span>
              </div>
              <p className="text-sm text-gray-600">Healing from the inside out</p>
            </div>
            <div>
              <h4 className="font-semibold text-black mb-3 text-sm">Learn</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-sm text-gray-600 hover:text-black transition-colors">Philosophy</a></li>
                <li><a href="#" className="text-sm text-gray-600 hover:text-black transition-colors">The Process</a></li>
                <li><a href="#" className="text-sm text-gray-600 hover:text-black transition-colors">Isaiah's Story</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-black mb-3 text-sm">Tools</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-sm text-gray-600 hover:text-black transition-colors">GlowGPT</a></li>
                <li><a href="#" className="text-sm text-gray-600 hover:text-black transition-colors">The Book</a></li>
                <li><a href="#" className="text-sm text-gray-600 hover:text-black transition-colors">Resources</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-black mb-3 text-sm">Connect</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-sm text-gray-600 hover:text-black transition-colors">Community</a></li>
                <li><a href="#" className="text-sm text-gray-600 hover:text-black transition-colors">ARSA Foundation</a></li>
                <li><a href="#" className="text-sm text-gray-600 hover:text-black transition-colors">YouTube</a></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-gray-200 text-center">
            <p className="text-sm text-gray-500">© 2025 The Glow Project. You are not Chaos. You are the light that sees it.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}