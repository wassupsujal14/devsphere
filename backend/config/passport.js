const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const GitHubStrategy = require('passport-github2').Strategy;
const User = require('../models/user');
const bcrypt = require('bcryptjs');

// Serialize user
passport.serializeUser((user, done) => {
  done(null, user.id);
});

passport.deserializeUser(async (id, done) => {
  try {
    const user = await User.findById(id);
    done(null, user);
  } catch (err) {
    done(err, null);
  }
});

// Google Strategy
passport.use(new GoogleStrategy({
    clientID: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL: '/api/auth/google/callback'
  },
  async (accessToken, refreshToken, profile, done) => {
    try {
      // Check if user exists
      let user = await User.findOne({ email: profile.emails[0].value });

      if (user) {
        return done(null, user);
      }

      // Create new user
      const randomPassword = await bcrypt.hash(Math.random().toString(36), 10);
      
      user = new User({
        username: profile.displayName.replace(/\s+/g, '').toLowerCase() + Math.floor(Math.random() * 1000),
        email: profile.emails[0].value,
        password: randomPassword,
        googleId: profile.id
      });

      await user.save();
      done(null, user);
    } catch (err) {
      done(err, null);
    }
  }
));

// GitHub Strategy
passport.use(new GitHubStrategy({
    clientID: process.env.GITHUB_CLIENT_ID,
    clientSecret: process.env.GITHUB_CLIENT_SECRET,
    callbackURL: '/api/auth/github/callback'
  },
  async (accessToken, refreshToken, profile, done) => {
    try {
      const email = profile.emails && profile.emails[0] ? profile.emails[0].value : `${profile.username}@github.com`;
      
      let user = await User.findOne({ email });

      if (user) {
        return done(null, user);
      }

      const randomPassword = await bcrypt.hash(Math.random().toString(36), 10);
      
      user = new User({
        username: profile.username || profile.displayName.replace(/\s+/g, '').toLowerCase(),
        email: email,
        password: randomPassword,
        githubId: profile.id
      });

      await user.save();
      done(null, user);
    } catch (err) {
      done(err, null);
    }
  }
));

module.exports = passport;