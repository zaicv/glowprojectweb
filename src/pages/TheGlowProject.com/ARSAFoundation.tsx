import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { GlowProjectNav } from "@/components/TheGlowProject/GlowProjectNav";
import { GlowProjectFooter } from "@/components/TheGlowProject/GlowProjectFooter";
import {
  Heart,
  Users,
  FileText,
  Stethoscope,
  BookOpen,
  MessageCircle,
  Shield,
  Info,
  ArrowRight,
  Sparkles,
  UserCircle,
  Baby,
  GraduationCap,
  CheckCircle2,
  Map,
  Phone,
  Mail,
} from "lucide-react";

export default function ARSAFoundation() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <div className="min-h-screen bg-white">
      <GlowProjectNav ctaLabel="Find Support" ctaHref="/arsafoundation" />

      {/* Hero Section */}
      <section className="relative pt-32 pb-24 px-6">
        <div className={`max-w-5xl mx-auto text-center transition-all duration-700 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <div className="inline-flex items-center gap-2 bg-[#d81b1b]/5 px-4 py-2 rounded-full mb-8 border border-[#d81b1b]/20">
            <Shield className="w-4 h-4 text-[#d81b1b]" />
            <span className="text-sm font-medium text-gray-700">You are safe here</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight text-black tracking-tight">
            Welcome to the<br />ARSA Foundation
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            A safe space for anyone affected by <span className="font-semibold text-black">Aberrant Right Subclavian Artery</span>. Here, you'll find others who understand, verified medical info, and a path toward clarity and calm.
          </p>

          <div className="bg-[#d81b1b]/5 border border-[#d81b1b]/20 rounded-2xl p-6 mb-12 max-w-2xl mx-auto">
            <p className="text-lg font-medium text-black mb-2">
              You are SAFE. Don't worry.
            </p>
            <p className="text-gray-700">
              There is relief, there is health, and more than that — there is hope.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 justify-center items-center">
            <Button 
              size="lg" 
              className="bg-[#d81b1b] text-white hover:bg-[#c01515] rounded-xl px-8 py-6 text-base font-medium transition-all shadow-sm hover:shadow-md active:scale-95 group"
            >
              <Users className="mr-2 w-5 h-5" />
              Join Our Community
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button 
              size="lg" 
              className="bg-white text-black hover:bg-gray-50 rounded-xl px-8 py-6 text-base font-medium transition-all border border-gray-200 shadow-sm hover:shadow-md active:scale-95"
            >
              Find a Doctor
            </Button>
          </div>
        </div>
      </section>

      {/* Getting Started Section */}
      <section className="py-24 px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-black tracking-tight">How to Get Started</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Your journey to connection and support begins here
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <Card className="hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-[#d81b1b] bg-white rounded-2xl overflow-hidden">
              <CardContent className="p-6">
                <div className="w-12 h-12 rounded-xl bg-[#d81b1b] flex items-center justify-center mb-4">
                  <span className="text-xl font-bold text-white">1</span>
                </div>
                <h3 className="text-lg font-bold mb-2 text-black">Choose Your Role</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Let us know if you're a patient, parent/caregiver, or medical researcher so we can connect you to the right resources.
                </p>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <UserCircle className="w-4 h-4 text-[#d81b1b]" />
                    Patient
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <Baby className="w-4 h-4 text-[#d81b1b]" />
                    Parent/Caregiver
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <GraduationCap className="w-4 h-4 text-[#d81b1b]" />
                    Medical Ally
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-[#d81b1b] bg-white rounded-2xl overflow-hidden">
              <CardContent className="p-6">
                <div className="w-12 h-12 rounded-xl bg-black flex items-center justify-center mb-4">
                  <span className="text-xl font-bold text-white">2</span>
                </div>
                <h3 className="text-lg font-bold mb-2 text-black">Share Your Story</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Introduce yourself and share as much or as little as you're comfortable with. You're among people who understand.
                </p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-4 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  Join Introductions
                </Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-[#d81b1b] bg-white rounded-2xl overflow-hidden">
              <CardContent className="p-6">
                <div className="w-12 h-12 rounded-xl bg-[#d81b1b] flex items-center justify-center mb-4">
                  <span className="text-xl font-bold text-white">3</span>
                </div>
                <h3 className="text-lg font-bold mb-2 text-black">Explore Resources</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Access verified medical information, find specialists, connect with support groups, and discover coping tools.
                </p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-4 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  View Resources
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Community Guidelines */}
          <Card className="border border-gray-200 bg-white rounded-2xl">
            <CardContent className="p-8">
              <div className="flex items-start gap-4 mb-6">
                <div className="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center flex-shrink-0">
                  <Shield className="w-6 h-6 text-black" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-black mb-2">Our Community Guidelines</h3>
                  <p className="text-sm text-gray-600">
                    This is a space built on trust, respect, and truth — no spam, medical advice, or fearmongering
                  </p>
                </div>
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#d81b1b] flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-black">Be kind and respectful</p>
                    <p className="text-xs text-gray-600">We're all here to support each other</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#d81b1b] flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-black">Share experiences, not medical advice</p>
                    <p className="text-xs text-gray-600">Only cite verified sources</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#d81b1b] flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-black">Protect your privacy</p>
                    <p className="text-xs text-gray-600">Share only what feels comfortable</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#d81b1b] flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-black">This complements medical care</p>
                    <p className="text-xs text-gray-600">Not a substitute for professional treatment</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Understanding ARSA Section */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-black tracking-tight">Understanding ARSA</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Clear, accessible information about Aberrant Right Subclavian Artery
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 mb-12">
            <Card className="border border-gray-200 bg-white rounded-2xl">
              <CardContent className="p-8">
                <div className="bg-[#d81b1b]/10 w-12 h-12 rounded-xl flex items-center justify-center mb-6">
                  <Info className="w-6 h-6 text-[#d81b1b]" />
                </div>
                <h3 className="text-2xl font-bold mb-4 text-black">What is ARSA?</h3>
                <p className="text-gray-700 leading-relaxed mb-4">
                  Aberrant Right Subclavian Artery (ARSA) is a congenital vascular anomaly where the right subclavian artery arises abnormally from the aortic arch. It affects approximately 0.5-2% of the population.
                </p>
                <p className="text-gray-700 leading-relaxed">
                  While many people with ARSA are asymptomatic, some may experience swallowing difficulties (dysphagia) or respiratory symptoms due to compression of the esophagus or trachea.
                </p>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 bg-white rounded-2xl">
              <CardContent className="p-8">
                <div className="bg-black/10 w-12 h-12 rounded-xl flex items-center justify-center mb-6">
                  <Stethoscope className="w-6 h-6 text-black" />
                </div>
                <h3 className="text-2xl font-bold mb-4 text-black">Common Symptoms</h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#d81b1b] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">Difficulty swallowing (dysphagia)</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#d81b1b] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">Chest discomfort or pressure</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#d81b1b] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">Breathing difficulties</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#d81b1b] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">Coughing or stridor (in children)</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#d81b1b] flex-shrink-0 mt-2" />
                    <span className="text-sm text-gray-700">Many cases are asymptomatic</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>

          <Card className="border border-gray-200 bg-gray-50 rounded-2xl">
            <CardContent className="p-8">
              <h3 className="text-xl font-bold mb-4 text-black">Diagnosis & Treatment</h3>
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="font-semibold text-black mb-3 text-sm">Diagnostic Methods</h4>
                  <ul className="space-y-2">
                    <li className="flex items-center gap-2 text-sm text-gray-700">
                      <CheckCircle2 className="w-4 h-4 text-[#d81b1b]" />
                      CT Angiography (CTA)
                    </li>
                    <li className="flex items-center gap-2 text-sm text-gray-700">
                      <CheckCircle2 className="w-4 h-4 text-[#d81b1b]" />
                      MRI/MRA
                    </li>
                    <li className="flex items-center gap-2 text-sm text-gray-700">
                      <CheckCircle2 className="w-4 h-4 text-[#d81b1b]" />
                      Barium swallow study
                    </li>
                    <li className="flex items-center gap-2 text-sm text-gray-700">
                      <CheckCircle2 className="w-4 h-4 text-[#d81b1b]" />
                      Echocardiography
                    </li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-black mb-3 text-sm">Treatment Options</h4>
                  <ul className="space-y-2">
                    <li className="flex items-center gap-2 text-sm text-gray-700">
                      <CheckCircle2 className="w-4 h-4 text-[#d81b1b]" />
                      Observation (if asymptomatic)
                    </li>
                    <li className="flex items-center gap-2 text-sm text-gray-700">
                      <CheckCircle2 className="w-4 h-4 text-[#d81b1b]" />
                      Surgical repair (if symptomatic)
                    </li>
                    <li className="flex items-center gap-2 text-sm text-gray-700">
                      <CheckCircle2 className="w-4 h-4 text-[#d81b1b]" />
                      Symptom management
                    </li>
                    <li className="flex items-center gap-2 text-sm text-gray-700">
                      <CheckCircle2 className="w-4 h-4 text-[#d81b1b]" />
                      Regular monitoring
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Resources Hub */}
      <section className="py-24 px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-black tracking-tight">Your Resource Hub</h2>
            <p className="text-lg text-gray-600">
              Everything you need in one place
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <Card className="group hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-[#d81b1b] bg-white rounded-2xl overflow-hidden cursor-pointer active:scale-[0.98]">
              <CardContent className="p-6">
                <div className="bg-[#d81b1b] w-11 h-11 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Map className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-bold mb-2 text-black">Doctor Directory</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Find specialists and clinics around the world who understand ARSA and can provide expert care.
                </p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-4 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  Find Doctors
                </Button>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-black bg-white rounded-2xl overflow-hidden cursor-pointer active:scale-[0.98]">
              <CardContent className="p-6">
                <div className="bg-black w-11 h-11 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <BookOpen className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-bold mb-2 text-black">Research & Studies</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Access peer-reviewed research, clinical studies, and the latest medical findings about ARSA.
                </p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-4 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  View Research
                </Button>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-[#d81b1b] bg-white rounded-2xl overflow-hidden cursor-pointer active:scale-[0.98]">
              <CardContent className="p-6">
                <div className="bg-[#d81b1b] w-11 h-11 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Heart className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-bold mb-2 text-black">Emotional Support</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Connect with others, share experiences, and find coping tools to manage stress and anxiety.
                </p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-4 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  Get Support
                </Button>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-black bg-white rounded-2xl overflow-hidden cursor-pointer active:scale-[0.98]">
              <CardContent className="p-6">
                <div className="bg-black w-11 h-11 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Users className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-bold mb-2 text-black">Parent Corner</h3>
                <p className="text-sm text-gray-600 mb-4">
                  A dedicated space for families caring for children with ARSA — resources, support, and shared stories.
                </p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-4 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  For Parents
                </Button>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-[#d81b1b] bg-white rounded-2xl overflow-hidden cursor-pointer active:scale-[0.98]">
              <CardContent className="p-6">
                <div className="bg-[#d81b1b] w-11 h-11 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-bold mb-2 text-black">Success Stories</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Read inspiring stories from others who've navigated ARSA — recovery, treatment, and hope.
                </p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-4 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  Read Stories
                </Button>
              </CardContent>
            </Card>

            <Card className="group hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-black bg-white rounded-2xl overflow-hidden cursor-pointer active:scale-[0.98]">
              <CardContent className="p-6">
                <div className="bg-black w-11 h-11 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <MessageCircle className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-bold mb-2 text-black">Ask & Share</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Post questions, share your experiences, and connect with others on the same journey.
                </p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-4 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  Join Discussion
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* You Are Not Alone Section */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <Card className="border-2 border-[#d81b1b] bg-gradient-to-br from-[#d81b1b]/5 to-white rounded-3xl overflow-hidden">
            <CardContent className="p-12 text-center">
              <div className="w-16 h-16 rounded-2xl bg-[#d81b1b] flex items-center justify-center mx-auto mb-6">
                <Heart className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-4 text-black tracking-tight">
                You Are Not Alone
              </h2>
              <p className="text-lg text-gray-700 mb-8 leading-relaxed">
                Thousands of people around the world are living with ARSA. This community exists so that no one has to face it in isolation. Whether you're newly diagnosed, a parent seeking answers, or a medical professional wanting to help — you belong here.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button 
                  size="lg" 
                  className="bg-[#d81b1b] text-white hover:bg-[#c01515] rounded-xl px-8 py-6 text-base font-medium transition-all shadow-sm hover:shadow-md active:scale-95"
                >
                  Join Our Community
                </Button>
                <Button 
                  size="lg" 
                  className="bg-white text-black hover:bg-gray-50 rounded-xl px-8 py-6 text-base font-medium transition-all border border-gray-200 shadow-sm hover:shadow-md active:scale-95"
                >
                  Share Your Story
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Contact & Get Involved */}
      <section className="py-24 px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-black tracking-tight">Get Involved</h2>
            <p className="text-lg text-gray-600">
              Help us build a world where no one faces ARSA alone
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <Card className="border border-gray-200 bg-white rounded-2xl hover:shadow-lg transition-all">
              <CardContent className="p-6 text-center">
                <div className="bg-[#d81b1b]/10 w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <Users className="w-6 h-6 text-[#d81b1b]" />
                </div>
                <h3 className="text-lg font-bold mb-2 text-black">Volunteer</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Help moderate, translate resources, or support community members
                </p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-3 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  Learn More
                </Button>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 bg-white rounded-2xl hover:shadow-lg transition-all">
              <CardContent className="p-6 text-center">
                <div className="bg-black/10 w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <GraduationCap className="w-6 h-6 text-black" />
                </div>
                <h3 className="text-lg font-bold mb-2 text-black">Research Partners</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Medical professionals: collaborate on studies and improve care
                </p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-3 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  Partner With Us
                </Button>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 bg-white rounded-2xl hover:shadow-lg transition-all">
              <CardContent className="p-6 text-center">
                <div className="bg-[#d81b1b]/10 w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <Heart className="w-6 h-6 text-[#d81b1b]" />
                </div>
                <h3 className="text-lg font-bold mb-2 text-black">Donate</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Support research, resources, and community building efforts
                </p>
                <Button className="w-full bg-gray-50 text-black hover:bg-gray-100 rounded-xl py-3 text-sm font-medium transition-all border border-gray-200 active:scale-95">
                  Support Us
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6 text-black tracking-tight">Questions? We're Here to Help</h2>
          <p className="text-lg text-gray-600 mb-10">
            Reach out to our team for support, information, or to get connected with resources
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-10">
            <a href="mailto:support@arsafoundation.org" className="inline-flex items-center gap-2 text-[#d81b1b] hover:text-[#c01515] transition-colors">
              <Mail className="w-5 h-5" />
              <span className="font-medium">support@arsafoundation.org</span>
            </a>
          </div>
          <Button 
            size="lg" 
            className="bg-black text-white hover:bg-gray-800 rounded-xl px-8 py-6 text-base font-medium transition-all shadow-sm hover:shadow-md active:scale-95"
          >
            Subscribe to Updates
          </Button>
        </div>
      </section>

      {/* Footer */}
      <GlowProjectFooter />

    </div>
  );
}
