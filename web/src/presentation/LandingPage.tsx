import React, { useState, useEffect } from 'react';
import { 
  Code2, 
  TerminalSquare, 
  Rocket, 
  ChevronRight, 
  PlayCircle,
  Trophy,
  Users,
  Github
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);

  // Handle transparent to blur navbar transition on scroll
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 font-sans selection:bg-cyan-500/30">
      
      {/* =======================
          NAVIGATION BAR
          ======================= */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${isScrolled ? 'bg-slate-950/80 backdrop-blur-md border-b border-slate-800 py-4 shadow-lg' : 'bg-transparent py-6'}`}>
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
          
          <div className="flex items-center cursor-pointer">
            <img src="/logo.png" alt="CipherPage" className="h-16" />
          </div>
          
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
            <a href="#courses" className="hover:text-cyan-400 transition-colors">Courses</a>
            <a href="#framework" className="hover:text-cyan-400 transition-colors">Framework</a>
            <a href="#pricing" className="hover:text-cyan-400 transition-colors">Pricing</a>
          </div>
          
          <div className="flex items-center gap-4">
            <button className="hidden md:block text-sm font-medium text-slate-300 hover:text-white transition-colors">
              Sign In
            </button>
            <button className="px-5 py-2.5 text-sm font-semibold rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 transition-all shadow-[0_0_15px_rgba(34,211,238,0.4)] hover:shadow-[0_0_25px_rgba(34,211,238,0.6)]">
              Register
            </button>
          </div>
        </div>
      </nav>

      {/* =======================
          HERO SECTION
          ======================= */}
      <section className="relative pt-40 pb-20 md:pt-52 md:pb-32 overflow-hidden">
        {/* Abstract Background Glows */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-purple-600/20 rounded-full blur-[120px] pointer-events-none"></div>
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-cyan-500/10 rounded-full blur-[100px] pointer-events-none"></div>
        
        <div className="max-w-7xl mx-auto px-6 relative z-10 text-center">
          
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-900/80 border border-slate-700 text-sm font-medium text-cyan-400 mb-8 shadow-sm">
            <Rocket size={16} />
            <span>Welcome to the future of coding education.</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 leading-tight">
            Stop Watching.<br className="hidden md:block"/> Start <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-emerald-400">Coding</span>.
          </h1>
          
          <p className="text-lg md:text-xl text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            Master software engineering through our <span className="text-white font-semibold">LAG (Learn, Apply, Grow)</span> framework. Ditch passive tutorials and build real-world systems directly in your browser.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button className="w-full sm:w-auto px-8 py-4 rounded-xl font-semibold bg-gradient-to-r from-cyan-500 to-cyan-400 text-slate-950 hover:to-cyan-300 transition-all shadow-[0_0_20px_rgba(34,211,238,0.4)] flex items-center justify-center gap-2 group">
              Start Coding for Free
              <ChevronRight size={20} className="group-hover:translate-x-1 transition-transform" />
            </button>
            <button className="w-full sm:w-auto px-8 py-4 rounded-xl font-semibold bg-slate-800 text-white border border-slate-700 hover:bg-slate-700 hover:border-slate-600 transition-all flex items-center justify-center gap-2">
              Explore Tracks
            </button>
          </div>
        </div>
      </section>

      {/* =======================
          LAG FRAMEWORK SECTION
          ======================= */}
      <section id="framework" className="py-24 bg-slate-900 border-y border-slate-800">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">The <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500">LAG</span> Philosophy</h2>
            <p className="text-slate-400 text-lg max-w-2xl mx-auto">An optimized feedback loop engineered to transform absolute beginners into elite developers.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            {/* COLUMN 1: LEARN */}
            <div className="bg-slate-950 p-8 rounded-2xl border border-slate-800 hover:border-cyan-500/50 transition-colors group relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-[50px] group-hover:bg-cyan-500/20 transition-colors"></div>
              <div className="w-14 h-14 bg-cyan-500/10 rounded-xl flex items-center justify-center mb-6 border border-cyan-500/20">
                <PlayCircle className="text-cyan-400" size={28} />
              </div>
              <h3 className="text-2xl font-bold mb-3 text-white">LEARN</h3>
              <p className="text-slate-400 leading-relaxed">
                Absorb knowledge through premium, high-density video tutorials. Access step-by-step documentation, expert-led architectural breakdowns, and pristine source code templates.
              </p>
            </div>

            {/* COLUMN 2: APPLY */}
            <div className="bg-slate-950 p-8 rounded-2xl border border-slate-800 hover:border-purple-500/50 transition-colors group relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-[50px] group-hover:bg-purple-500/20 transition-colors"></div>
              <div className="w-14 h-14 bg-purple-500/10 rounded-xl flex items-center justify-center mb-6 border border-purple-500/20">
                <TerminalSquare className="text-purple-400" size={28} />
              </div>
              <h3 className="text-2xl font-bold mb-3 text-white">APPLY</h3>
              <p className="text-slate-400 leading-relaxed">
                Don't just watch—write code. Use our integrated browser workspaces and instant compiler testing to tackle real-world debugging challenges right as you learn them.
              </p>
            </div>

            {/* COLUMN 3: GROW */}
            <div className="bg-slate-950 p-8 rounded-2xl border border-slate-800 hover:border-emerald-500/50 transition-colors group relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-[50px] group-hover:bg-emerald-500/20 transition-colors"></div>
              <div className="w-14 h-14 bg-emerald-500/10 rounded-xl flex items-center justify-center mb-6 border border-emerald-500/20">
                <Trophy className="text-emerald-400" size={28} />
              </div>
              <h3 className="text-2xl font-bold mb-3 text-white">GROW</h3>
              <p className="text-slate-400 leading-relaxed">
                Forge a standout portfolio. Unlock robust career-building tools, generate verified milestone badges, and get matched with tech companies seeking proven open-source contributors.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* =======================
          SOCIAL PROOF / STATS
          ======================= */}
      <section className="py-24 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-12 md:gap-4 divide-y md:divide-y-0 md:divide-x divide-slate-800">
            <div className="text-center px-4 pt-6 md:pt-0">
              <div className="text-4xl md:text-5xl font-extrabold text-white mb-2 tracking-tight">100k+</div>
              <div className="text-slate-400 font-medium">Code Submissions</div>
            </div>
            <div className="text-center px-4 pt-6 md:pt-0">
              <div className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 mb-2 tracking-tight">50+</div>
              <div className="text-slate-400 font-medium">Career Tracks</div>
            </div>
            <div className="text-center px-4 pt-6 md:pt-0">
              <div className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 mb-2 tracking-tight">10k+</div>
              <div className="text-slate-400 font-medium">Active Students</div>
            </div>
            <div className="text-center px-4 pt-6 md:pt-0">
              <div className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400 mb-2 tracking-tight">99%</div>
              <div className="text-slate-400 font-medium">Uptime Compiler</div>
            </div>
          </div>
        </div>
      </section>

      {/* =======================
          GLOBAL FOOTER
          ======================= */}
      <footer className="border-t border-slate-800 bg-slate-950 pt-16 pb-8">
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          
          {/* Brand Info */}
          <div className="md:col-span-1">
            <div className="flex items-center mb-6">
              <img src="/logo.png" alt="CipherPage" className="h-14" />
            </div>
            <p className="text-slate-400 text-sm leading-relaxed mb-6">
              Empowering the next generation of software engineers through our LAG framework. Learn, Apply, and Grow with us.
            </p>
            <div className="flex gap-4">
              <a href="#" className="text-slate-400 hover:text-cyan-400 transition-colors"><Github size={20} /></a>
              <a href="#" className="text-slate-400 hover:text-cyan-400 transition-colors"><Users size={20} /></a>
            </div>
          </div>
          
          {/* Links */}
          <div>
            <h4 className="text-white font-semibold mb-6">Platform</h4>
            <ul className="space-y-4 text-sm text-slate-400">
              <li><a href="#" className="hover:text-cyan-400 transition-colors">All Courses</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Workspace</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Challenges</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Pricing</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-white font-semibold mb-6">Company</h4>
            <ul className="space-y-4 text-sm text-slate-400">
              <li><a href="#" className="hover:text-cyan-400 transition-colors">About Us</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Careers</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Blog</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Contact</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-white font-semibold mb-6">Legal</h4>
            <ul className="space-y-4 text-sm text-slate-400">
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Terms of Service</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Cookie Policy</a></li>
            </ul>
          </div>
        </div>
        
        {/* Copyright */}
        <div className="max-w-7xl mx-auto px-6 border-t border-slate-800/50 pt-8 flex flex-col md:flex-row items-center justify-between text-sm text-slate-500">
          <p>&copy; {new Date().getFullYear()} CipherPage Inc. All rights reserved.</p>
          <div className="flex items-center gap-1 mt-4 md:mt-0">
            Made with <span className="text-cyan-400 mx-1">♥</span> for developers
          </div>
        </div>
      </footer>
    </div>
  );
};
