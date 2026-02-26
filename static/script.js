// ==========================================
// THEME TOGGLE
// ==========================================
const themeToggle = document.getElementById('theme-toggle');
const html = document.documentElement;
const logo = document.getElementById('logo');

// Update logo based on theme
function updateLogo(theme) {
  if (theme === 'dark') {
    logo.src = '/static/assets/MLS Logo Dark.png'; // Light logo for dark mode
  } else {
    logo.src = '/static/assets/MLS Logo.png'; // Dark logo for light mode
  }
}

// Check for saved theme preference or default to 'dark'
const currentTheme = localStorage.getItem('theme') || 'dark';
html.setAttribute('data-theme', currentTheme);
updateLogo(currentTheme);

themeToggle.addEventListener('click', () => {
  const currentTheme = html.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  
  html.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  updateLogo(newTheme);
});

// ==========================================
// NEURAL NETWORK CANVAS ANIMATION
// ==========================================
const canvas = document.getElementById('neural-network');
const ctx = canvas.getContext('2d');

// Set canvas size
function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// Neural network nodes
class Node {
  constructor() {
    this.x = Math.random() * canvas.width;
    this.y = Math.random() * canvas.height;
    this.vx = (Math.random() - 0.5) * 0.5;
    this.vy = (Math.random() - 0.5) * 0.5;
    this.radius = Math.random() * 2 + 1;
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;

    // Bounce off edges
    if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
    if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
  }

  draw() {
    const theme = html.getAttribute('data-theme');
    const nodeColor = theme === 'dark' 
      ? 'rgba(249, 115, 22, 0.8)' 
      : 'rgba(249, 115, 22, 0.6)';
    
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = nodeColor;
    ctx.fill();
  }
}

// Create nodes
const nodeCount = window.innerWidth > 768 ? 80 : 40;
const nodes = [];
for (let i = 0; i < nodeCount; i++) {
  nodes.push(new Node());
}

// Draw connections between nearby nodes
function drawConnections() {
  const theme = html.getAttribute('data-theme');
  const lineColor = theme === 'dark' 
    ? 'rgba(248, 250, 252, 0.08)' 
    : 'rgba(15, 23, 42, 0.08)';
  
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dx = nodes[i].x - nodes[j].x;
      const dy = nodes[i].y - nodes[j].y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < 150) {
        ctx.beginPath();
        ctx.moveTo(nodes[i].x, nodes[i].y);
        ctx.lineTo(nodes[j].x, nodes[j].y);
        ctx.strokeStyle = lineColor;
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    }
  }
}

// Animation loop
function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  drawConnections();
  
  nodes.forEach(node => {
    node.update();
    node.draw();
  });

  requestAnimationFrame(animate);
}

animate();

// ==========================================
// SCROLL ANIMATIONS
// ==========================================
const observerOptions = {
  threshold: 0.15,
  rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, observerOptions);

// Observe all fade-in elements
const fadeElements = document.querySelectorAll('.fade-in');
fadeElements.forEach(el => observer.observe(el));

// ==========================================
// CARD TILT EFFECT
// ==========================================
const cards = document.querySelectorAll('[data-tilt]');

cards.forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    const rotateX = (y - centerY) / 10;
    const rotateY = (centerX - x) / 10;
    
    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-10px)`;
  });
  
  card.addEventListener('mouseleave', () => {
    card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
  });
});

// ==========================================
// SMOOTH SCROLL
// ==========================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      const offsetTop = target.offsetTop - 80; // Account for navbar height
      window.scrollTo({
        top: offsetTop,
        behavior: 'smooth'
      });
    }
  });
});

// ==========================================
// CURSOR GLOW EFFECT (Optional Enhancement)
// ==========================================
let mouseX = 0;
let mouseY = 0;

document.addEventListener('mousemove', (e) => {
  mouseX = e.clientX;
  mouseY = e.clientY;
});

// Add glow to cards based on mouse position
cards.forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const glow = card.querySelector('.card-glow');
    if (glow) {
      glow.style.background = `radial-gradient(circle at ${x}px ${y}px, var(--accent-glow) 0%, transparent 50%)`;
    }
  });
});

// ==========================================
// NAVBAR SCROLL EFFECT
// ==========================================
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
  const currentScroll = window.pageYOffset;
  
  if (currentScroll > 100) {
    navbar.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.1)';
  } else {
    navbar.style.boxShadow = 'none';
  }
  
  lastScroll = currentScroll;
});

// ==========================================
// PERFORMANCE OPTIMIZATION
// ==========================================
// Pause animations when tab is not visible
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    // Pause heavy animations
    canvas.style.opacity = '0';
  } else {
    canvas.style.opacity = '0.6';
  }
});

// Reduce particle count on mobile
if (window.innerWidth <= 768) {
  // Already handled in node count above
  console.log('Mobile optimizations applied');
}

console.log('🧠 Machine Learning Society website loaded successfully!');
