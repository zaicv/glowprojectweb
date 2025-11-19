import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { GlowProjectNav } from "@/components/TheGlowProject/GlowProjectNav";
import { GlowProjectFooter } from "@/components/TheGlowProject/GlowProjectFooter";
import {
  Sparkles,
  ArrowRight,
  Sun,
  Moon,
  Eye,
  MessageSquare,
  Target,
  Heart,
  Zap,
  Brain,
  Wind,
  CheckCircle2,
  Play,
  Book,
  Headphones,
  Video,
  Lightbulb,
  Users,
  Pen,
} from "lucide-react";

export default function GlowProcessPage() {
  const navigate = useNavigate();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <div className="min-h-screen bg-white">
      <GlowProjectNav ctaLabel="Start Free" ctaHref="/glowgpt" />

      {/* Hero Section */}
      <section className="relative pt-32 pb-24 px-6">
        <div className={`max-w-5xl mx-auto text-center transition-all duration-700 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <div className="inline-flex items-center gap-2 bg-[#e1e65c]/10 px-4 py-2 rounded-full mb-8 border border-[#e1e65c]/20">
            <Sparkles className="w-4 h-4 text-[#e1e65c]" />
            <span className="text-sm font-medium text-gray-700">Your personalized healing framework</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight text-black tracking-tight">
            The Glow Process
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            A fluid, personalized framework for reshaping consciousness — helping you clear limiting beliefs, rewire your nervous system, and connect with your ideal future
          </p>

          <div className="bg-[#e1e65c]/5 border border-[#e1e65c]/20 rounded-2xl p-6 mb-12 max-w-2xl mx-auto">
            <p className="text-gray-700 leading-relaxed">
              <span className="font-semibold text-black">This isn't a one-size-fits-all program.</span> The Glow Process adapts to you — whether you're healing from trauma, managing anxiety, rebuilding confidence, or creating a life you actually want to live.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 justify-center items-center">
            <Button
              size="lg"
              onClick={() => navigate("/glowgpt")}
              className="bg-[#e1e65c] text-black hover:bg-[#d4d950] rounded-xl px-8 py-6 text-base font-medium transition-all shadow-sm hover:shadow-md active:scale-95 group"
            >
              <Pen className="mr-2 w-5 h-5" />
              Create Your Process
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button
              size="lg"
              onClick={() => navigate("/the-glow-foundation")}
              className="bg-white text-black hover:bg-gray-50 rounded-xl px-8 py-6 text-base font-medium transition-all border border-gray-200 shadow-sm hover:shadow-md active:scale-95"
            >
              Watch How It Works
            </Button>
          </div>
        </div>
      </section>

      {/* The Dual Force Model */}
      <section className="py-24 px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-black tracking-tight">First, Understand the Two Forces</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Everything starts with recognizing what's driving you
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-12">
            <Card className="group hover:shadow-lg transition-all duration-300 border border-gray-200 bg-white rounded-2xl overflow-hidden">
              <CardContent className="p-8">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-14 h-14 rounded-xl bg-black flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Moon className="w-7 h-7 text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-black">Chaos</h3>
                    <p className="text-sm text-gray-500">The survival mind</p>
                  </div>
                </div>
                <p className="text-gray-700 leading-relaxed mb-4">
                  The voice that says "you're not enough." The mental loops of anxiety, perfectionism, and self-doubt. The beliefs you absorbed as a child that now run your life on autopilot.
                </p>
                <div className="space-y-2 mb-4">
                  <div className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-black flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">"I need to be perfect or I don't matter"</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-black flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">"Everyone will leave me"</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-black flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">"I can't trust my body"</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-black flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">"I'm weird, awkward, too much"</span>
                  </div>
                </div>
                <p className="text-sm text-gray-600 italic">
                  Chaos isn't evil — it once kept you safe. But now it's keeping you small.
                </p>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-[#e1e65c] bg-white rounded-2xl overflow-hidden">
              <CardContent className="p-8">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-14 h-14 rounded-xl bg-[#e1e65c] flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Sun className="w-7 h-7 text-black" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-black">The Glow</h3>
                    <p className="text-sm text-gray-500">Pure awareness</p>
                  </div>
                </div>
                <p className="text-gray-700 leading-relaxed mb-4">
                  The part of you that simply exists — right here, right now. The awareness that watches your thoughts without being consumed by them. The peace underneath all the noise.
                </p>
                <div className="space-y-2 mb-4">
                  <div className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#e1e65c] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">"I am here, and I am safe"</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#e1e65c] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">"I am enough as I am right now"</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#e1e65c] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">"My body is strong and resilient"</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#e1e65c] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">"I trust myself completely"</span>
                  </div>
                </div>
                <p className="text-sm text-gray-600 italic">
                  The Glow was never gone — you just forgot how to feel it.
                </p>
              </CardContent>
            </Card>
          </div>

          <Card className="border-2 border-[#e1e65c] bg-gradient-to-br from-[#e1e65c]/5 to-white rounded-2xl">
            <CardContent className="p-8 text-center">
              <h3 className="text-2xl font-bold text-black mb-4">The Shift</h3>
              <p className="text-lg text-gray-700 leading-relaxed max-w-2xl mx-auto mb-4">
                You are not Chaos. You are the awareness that sees it.
              </p>
              <p className="text-gray-600">
                The Glow Process teaches you to recognize Chaos, disidentify from it, and return to presence — over and over, until it becomes your new default.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-black tracking-tight">How The Process Works</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Seven phases that rewire your nervous system and reshape your mind
            </p>
          </div>

          <div className="space-y-6">
            {/* Phase 1 */}
            <Card className="border border-gray-200 hover:border-[#70ac85] bg-white rounded-2xl overflow-hidden hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="flex items-start gap-6">
                  <div className="w-14 h-14 rounded-xl bg-[#70ac85] flex items-center justify-center flex-shrink-0">
                    <Wind className="w-7 h-7 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-2xl font-bold text-black">1. Body Release</h3>
                      <span className="text-sm text-gray-500">Ground into safety</span>
                    </div>
                    <p className="text-gray-700 leading-relaxed mb-4">
                      Sit up straight. Release tension from your face, shoulders, back. Breathe deeply into your diaphragm. Hug yourself. Play calming music. Create physical safety before anything else.
                    </p>
                    <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                      <p className="text-sm text-gray-700"><span className="font-semibold">Why:</span> You can't heal a mind in a dysregulated body. This activates your parasympathetic nervous system — the "rest and digest" mode.</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Phase 2 */}
            <Card className="border border-gray-200 hover:border-[#e1e65c] bg-white rounded-2xl overflow-hidden hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="flex items-start gap-6">
                  <div className="w-14 h-14 rounded-xl bg-[#e1e65c] flex items-center justify-center flex-shrink-0">
                    <Eye className="w-7 h-7 text-black" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-2xl font-bold text-black">2. Now Meditation</h3>
                      <span className="text-sm text-gray-500">Anchor in the present</span>
                    </div>
                    <p className="text-gray-700 leading-relaxed mb-4">
                      There is no past except in your mind. The future is just a projection. Let go of the chaos contaminating your thoughts. Focus attention in the Now — where you actually exist.
                    </p>
                    <div className="bg-[#e1e65c]/10 rounded-xl p-4 border border-[#e1e65c]/20">
                      <p className="text-sm text-gray-700"><span className="font-semibold">Why:</span> Anxiety lives in the future. Depression lives in the past. Peace lives right here, right now.</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Phase 3 */}
            <Card className="border border-gray-200 hover:border-[#1b86d8] bg-white rounded-2xl overflow-hidden hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="flex items-start gap-6">
                  <div className="w-14 h-14 rounded-xl bg-[#1b86d8] flex items-center justify-center flex-shrink-0">
                    <Lightbulb className="w-7 h-7 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-2xl font-bold text-black">3. Realign & Remember</h3>
                      <span className="text-sm text-gray-500">Reconnect with truth</span>
                    </div>
                    <p className="text-gray-700 leading-relaxed mb-4">
                      Who are you really? Remember your evidence — what you've survived, overcome, accomplished. Look at your reminders (finger anchors, photos, playlists). Convince yourself with proof, not hope.
                    </p>
                    <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                      <p className="text-sm text-gray-700"><span className="font-semibold">Example:</span> "I've survived multiple heart surgeries. I'm still here. I've got this. There is no doubt."</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Phase 4 */}
            <Card className="border border-gray-200 hover:border-black bg-white rounded-2xl overflow-hidden hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="flex items-start gap-6">
                  <div className="w-14 h-14 rounded-xl bg-black flex items-center justify-center flex-shrink-0">
                    <Heart className="w-7 h-7 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-2xl font-bold text-black">4. Self-Compassion & Gratitude</h3>
                      <span className="text-sm text-gray-500">Love yourself first</span>
                    </div>
                    <p className="text-gray-700 leading-relaxed mb-4">
                      Look at what makes you happy. Remember moments of joy. Feel gratitude for your body, your survival, your support. Practice speaking kindly to yourself — you're the only one who's always there.
                    </p>
                    <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                      <p className="text-sm text-gray-700"><span className="font-semibold">Why:</span> You can't heal from a place of self-hatred. Compassion rewires shame patterns.</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Phase 5 */}
            <Card className="border border-gray-200 hover:border-[#e1e65c] bg-white rounded-2xl overflow-hidden hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="flex items-start gap-6">
                  <div className="w-14 h-14 rounded-xl bg-[#e1e65c] flex items-center justify-center flex-shrink-0">
                    <MessageSquare className="w-7 h-7 text-black" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-2xl font-bold text-black">5. Affirmations</h3>
                      <span className="text-sm text-gray-500">Speak new beliefs into existence</span>
                    </div>
                    <p className="text-gray-700 leading-relaxed mb-4">
                      Your nervous system responds to language. Speak the truth you want to embody — out loud, with conviction. Use physical anchors. Repeat until your body believes it.
                    </p>
                    <div className="grid md:grid-cols-2 gap-3 mb-4">
                      <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <p className="text-xs font-semibold text-gray-500 mb-1">Body Safety</p>
                        <p className="text-sm text-gray-700">"I trust my body completely"</p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <p className="text-xs font-semibold text-gray-500 mb-1">Self-Worth</p>
                        <p className="text-sm text-gray-700">"I am enough as I am"</p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <p className="text-xs font-semibold text-gray-500 mb-1">Chaos</p>
                        <p className="text-sm text-gray-700">"I am not Chaos. I am Isaiah."</p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                        <p className="text-xs font-semibold text-gray-500 mb-1">Power</p>
                        <p className="text-sm text-gray-700">"I possess the power of the Glow"</p>
                      </div>
                    </div>
                    <div className="bg-[#e1e65c]/10 rounded-xl p-4 border border-[#e1e65c]/20">
                      <p className="text-sm text-gray-700"><span className="font-semibold">Science:</span> Neuroplasticity. Repeated affirmations create new neural pathways, literally rewiring your brain's default beliefs.</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Phase 6 */}
            <Card className="border border-gray-200 hover:border-[#70ac85] bg-white rounded-2xl overflow-hidden hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="flex items-start gap-6">
                  <div className="w-14 h-14 rounded-xl bg-[#70ac85] flex items-center justify-center flex-shrink-0">
                    <Brain className="w-7 h-7 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-2xl font-bold text-black">6. Absorption</h3>
                      <span className="text-sm text-gray-500">Let it integrate</span>
                    </div>
                    <p className="text-gray-700 leading-relaxed mb-4">
                      Set intention to deeply accept everything you just affirmed. Visualize warm light radiating from within, enveloping your body. Feel it sinking into your nervous system, becoming part of you.
                    </p>
                    <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                      <p className="text-sm text-gray-700"><span className="font-semibold">Why:</span> Information without integration is just noise. This is where healing becomes embodied.</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Phase 7 */}
            <Card className="border border-gray-200 hover:border-[#e1e65c] bg-white rounded-2xl overflow-hidden hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="flex items-start gap-6">
                  <div className="w-14 h-14 rounded-xl bg-[#e1e65c] flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-7 h-7 text-black" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-2xl font-bold text-black">7. Visualization</h3>
                      <span className="text-sm text-gray-500">See your healed future</span>
                    </div>
                    <p className="text-gray-700 leading-relaxed mb-4">
                      Close your eyes. See yourself 6 months, 1 year from now — fully healed, living the life you want. Use all your senses. What do you see? Feel? Hear? Make it vivid. Make it real.
                    </p>
                    <div className="bg-[#e1e65c]/10 rounded-xl p-4 border border-[#e1e65c]/20 mb-4">
                      <p className="text-sm text-gray-700"><span className="font-semibold">Science:</span> Your brain doesn't know the difference between vivid imagination and reality. Mental rehearsal activates the same neural circuits as lived experience.</p>
                    </div>
                    <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                      <p className="text-sm text-gray-700"><span className="font-semibold">Example:</span> See yourself running with your daughter, carrying her on your shoulders, laughing. Feel the sun on your face. Hear her giggling. This is your future. Believe it.</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* It's Fluid & Personal */}
      <section className="py-24 px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-black tracking-tight">
              It's Yours to Shape
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              The Glow Process adapts to whatever you're healing from
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <Card className="border border-gray-200 bg-white rounded-2xl hover:shadow-lg transition-all">
              <CardContent className="p-6">
                <div className="w-12 h-12 rounded-xl bg-[#d81b1b]/10 flex items-center justify-center mb-4">
                  <Heart className="w-6 h-6 text-[#d81b1b]" />
                </div>
                <h3 className="font-bold text-black mb-2">Health Anxiety</h3>
                <p className="text-sm text-gray-700 leading-relaxed mb-3">
                  Rewire fear patterns around your body. Build affirmations for physical safety. Visualize yourself moving freely without panic.
                </p>
                <p className="text-xs text-gray-600 italic">"I trust my body completely. It is strong and has saved me."</p>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 bg-white rounded-2xl hover:shadow-lg transition-all">
              <CardContent className="p-6">
                <div className="w-12 h-12 rounded-xl bg-[#1b86d8]/10 flex items-center justify-center mb-4">
                  <Users className="w-6 h-6 text-[#1b86d8]" />
                </div>
                <h3 className="font-bold text-black mb-2">Relationship Healing</h3>
                <p className="text-sm text-gray-700 leading-relaxed mb-3">
                  Release attachment anxiety. Practice self-soothing. Affirm your worth independent of others' reactions.
                </p>
                <p className="text-xs text-gray-600 italic">"I am enough whether they stay or go. I emotionally support myself."</p>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 bg-white rounded-2xl hover:shadow-lg transition-all">
              <CardContent className="p-6">
                <div className="w-12 h-12 rounded-xl bg-[#70ac85]/10 flex items-center justify-center mb-4">
                  <Brain className="w-6 h-6 text-[#70ac85]" />
                </div>
                <h3 className="font-bold text-black mb-2">Self-Worth & Confidence</h3>
                <p className="text-sm text-gray-700 leading-relaxed mb-3">
                  Challenge "not enough" beliefs. Build evidence of your capabilities. Visualize yourself showing up fully.
                </p>
                <p className="text-xs text-gray-600 italic">"I don't need to be perfect. I just need to be me. I am the shit."</p>
              </CardContent>
            </Card>
          </div>

          <Card className="border-2 border-[#e1e65c] bg-gradient-to-br from-[#e1e65c]/5 to-white rounded-2xl">
            <CardContent className="p-8">
              <h3 className="text-2xl font-bold text-black mb-4 text-center">You Can Create a Process for Anything</h3>
              <div className="grid md:grid-cols-2 gap-4 mb-6">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#e1e65c] flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-black">Body image struggles</p>
                    <p className="text-xs text-gray-600">Rewire appearance-based worth</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#e1e65c] flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-black">Performance anxiety</p>
                    <p className="text-xs text-gray-600">Build confidence before presentations</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#e1e65c] flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-black">Trauma recovery</p>
                    <p className="text-xs text-gray-600">Process grief and rebuild safety</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#e1e65c] flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-black">Career transitions</p>
                    <p className="text-xs text-gray-600">Visualize success, embody it now</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#e1e65c] flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-black">Social anxiety</p>
                    <p className="text-xs text-gray-600">Practice being yourself without fear</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#e1e65c] flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-black">Life transitions</p>
                    <p className="text-xs text-gray-600">Navigate change with groundedness</p>
                  </div>
                </div>
              </div>
              <p className="text-center text-gray-700">
                Whatever patterns aren't serving you — you can rewire them. The Process is a tool you control.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Real Benefits */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-black tracking-tight">
              What Changes in Your Life
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              These aren't promises — they're what happens when you do the work
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <Card className="border border-gray-200 bg-white rounded-2xl hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="flex items-start gap-4 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-[#70ac85]/10 flex items-center justify-center flex-shrink-0">
                    <Brain className="w-5 h-5 text-[#70ac85]" />
                  </div>
                  <h3 className="text-xl font-bold text-black">Mental Clarity</h3>
                </div>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#70ac85] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">You recognize Chaos when it starts speaking</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#70ac85] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">Anxiety loops lose their power over you</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#70ac85] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">You stop living on autopilot</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#70ac85] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">Decision-making becomes easier</span>
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 bg-white rounded-2xl hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="flex items-start gap-4 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-[#e1e65c]/10 flex items-center justify-center flex-shrink-0">
                    <Heart className="w-5 h-5 text-[#e1e65c]" />
                  </div>
                  <h3 className="text-xl font-bold text-black">Emotional Regulation</h3>
                </div>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#e1e65c] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">You can self-soothe without needing external validation</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#e1e65c] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">Triggers don't hijack you anymore</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#e1e65c] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">You respond instead of react</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#e1e65c] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">Peace becomes your baseline, not the exception</span>
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 bg-white rounded-2xl hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="flex items-start gap-4 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-[#1b86d8]/10 flex items-center justify-center flex-shrink-0">
                    <Target className="w-5 h-5 text-[#1b86d8]" />
                  </div>
                  <h3 className="text-xl font-bold text-black">Body Connection</h3>
                </div>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#1b86d8] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">You trust your body's signals again</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#1b86d8] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">Physical anxiety (chest tightness, racing heart) diminishes</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#1b86d8] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">You feel safe in your own skin</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#1b86d8] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">Movement becomes joyful, not fearful</span>
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 bg-white rounded-2xl hover:shadow-lg transition-all">
              <CardContent className="p-8">
                <div className="flex items-start gap-4 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-[#70ac85]/10 flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-5 h-5 text-[#70ac85]" />
                  </div>
                  <h3 className="text-xl font-bold text-black">Life Changes</h3>
                </div>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#70ac85] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">You show up authentically in relationships</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#70ac85] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">You pursue what you actually want, not what you "should"</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#70ac85] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">Perfectionism loosens its grip</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#70ac85] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">You become your own best friend</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* How to Begin */}
      <section className="py-24 px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 text-black tracking-tight">
            Ready to Build Yours?
          </h2>
          <p className="text-lg text-gray-600 mb-10 max-w-2xl mx-auto">
            The Glow Process works when you make it personal. Here's how to start:
          </p>

          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <Card className="border border-gray-200 bg-white rounded-2xl hover:shadow-lg transition-all hover:border-[#70ac85]">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 rounded-xl bg-[#70ac85] flex items-center justify-center mx-auto mb-4">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-bold text-black mb-2">GlowGPT</h3>
                <p className="text-sm text-gray-600 mb-4">AI guides you through creating your personalized process step-by-step</p>
                <Button
                  onClick={() => navigate("/glowgpt")}
                  className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-3 text-sm font-medium transition-all border border-gray-200 active:scale-95"
                >
                  Start Free
                </Button>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 bg-white rounded-2xl hover:shadow-lg transition-all hover:border-[#e1e65c]">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 rounded-xl bg-[#e1e65c] flex items-center justify-center mx-auto mb-4">
                  <Book className="w-6 h-6 text-black" />
                </div>
                <h3 className="font-bold text-black mb-2">The Full Course</h3>
                <p className="text-sm text-gray-600 mb-4">8-week structured program with worksheets, videos, and community support</p>
                <Button
                  onClick={() => navigate("/the-glow-foundation")}
                  className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-3 text-sm font-medium transition-all border border-gray-200 active:scale-95"
                >
                  Learn More
                </Button>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 bg-white rounded-2xl hover:shadow-lg transition-all hover:border-[#1b86d8]">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 rounded-xl bg-[#1b86d8] flex items-center justify-center mx-auto mb-4">
                  <Video className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-bold text-black mb-2">Free Resources</h3>
                <p className="text-sm text-gray-600 mb-4">YouTube tutorials, guided meditations, and downloadable templates</p>
                <Button
                  onClick={() => navigate("/about")}
                  className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-3 text-sm font-medium transition-all border border-gray-200 active:scale-95"
                >
                  Explore
                </Button>
              </CardContent>
            </Card>
          </div>

          <Card className="border-2 border-[#e1e65c] bg-gradient-to-br from-[#e1e65c]/5 to-white rounded-2xl">
            <CardContent className="p-8">
              <h3 className="text-xl font-bold text-black mb-4">Just 10 Minutes a Day</h3>
              <p className="text-gray-700 mb-6 leading-relaxed">
                You don't need an hour. You don't need to be perfect. Start with 10 minutes — ground into your body, speak one affirmation, visualize one moment of peace. That's enough to begin rewiring your brain.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button
                  size="lg"
                  onClick={() => navigate("/glowgpt")}
                  className="bg-[#e1e65c] text-black hover:bg-[#d4d950] rounded-xl px-8 py-6 text-base font-medium transition-all shadow-sm hover:shadow-md active:scale-95"
                >
                  <Pen className="mr-2 w-5 h-5" />
                  Create My Process
                </Button>
                <Button
                  size="lg"
                  onClick={() => navigate("/about")}
                  className="bg-white text-black hover:bg-gray-50 rounded-xl px-8 py-6 text-base font-medium transition-all border border-gray-200 shadow-sm hover:shadow-md active:scale-95"
                >
                  Download Template
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <Card className="border-2 border-black bg-gradient-to-br from-gray-50 to-white rounded-3xl overflow-hidden">
            <CardContent className="p-12 text-center">
              <div className="w-16 h-16 rounded-2xl bg-black flex items-center justify-center mx-auto mb-6">
                <Sun className="w-8 h-8 text-[#e1e65c]" />
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-4 text-black tracking-tight">
                You Are Not Chaos
              </h2>
              <p className="text-lg text-gray-700 mb-8 leading-relaxed max-w-xl mx-auto">
                You are the awareness that sees it. The peace that holds it. The light that never left. The Glow Process is how you remember.
              </p>
              <Button
                size="lg"
                onClick={() => navigate("/the-glow-foundation")}
                className="bg-black text-white hover:bg-gray-800 rounded-xl px-8 py-6 text-base font-medium transition-all shadow-sm hover:shadow-md active:scale-95"
              >
                Begin Your Journey
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <GlowProjectFooter />

    </div>
  );
}
