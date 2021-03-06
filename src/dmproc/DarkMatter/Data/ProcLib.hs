-- -*- mode: haskell; -*-
-- All Rights Reserved.
--
--    Licensed under the Apache License, Version 2.0 (the "License");
--    you may not use this file except in compliance with the License.
--    You may obtain a copy of the License at
--
--        http://www.apache.org/licenses/LICENSE-2.0
--
--    Unless required by applicable law or agreed to in writing, software
--    distributed under the License is distributed on an "AS IS" BASIS,
--    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
--    See the License for the specific language governing permissions and
--    limitations under the License.

-- | Provides a series of numeric functions and combinators useful to
-- this project.
module DarkMatter.Data.ProcLib where

import DarkMatter.Data.Proc

imean :: (Fractional a) => Int -> a -> a -> a
imean n m0 e = m0 + ((e - m0) / (fromIntegral n))

-- | Computes the mean using an numerically stable algorithm:
-- @
--    meanₙ₊₁ = meanₙ + aₖ₊₁ - meanₙ
--                      ――――――――――――
--                          n+1
-- @
-- 
-- One possible way to verify the above equation is correct is solving
-- the following on x:
-- @
--     ₙ            ₙ₊₁
--    ∑ aₖ         ∑ aₖ
--     ₖ₌₁          ₖ₌₁
--   ―――――― + x = ――――――
--      n          n+1
-- @ 
mean :: (Fractional a) => Proc a a
mean = Auto (f 0 1)
  where f m0 n e = let m1 = imean n m0 e
                   in (m1, Auto (f m1 (n + 1)))

-- | Exponential weighted moving average
ewma :: (Fractional a) => a -> Proc a (Maybe a)
ewma k = Auto (f False 0)
  where f t m0 e
          | t         = (Just m1, Auto $ f t m1)
          | otherwise = m1 `seq` (Nothing, Auto $ f True e)
            where m1 = k * m0 + (1 - k) * e

-- | Approximates the SMA implementation by using EWMA with an alpha
-- value of `1-2/(n+1)`. As the ewma starts producing data right away,
-- we warmup the ewma by waiting (n+1)/2 (roughly the cycle of SMA)
-- events to arrive.
sma :: (Fractional a) => Int  -> Proc a (Maybe a)
sma n = Auto (f ((n+1) `div` 2) (ewma (1 - 2 / fromIntegral (n+1))))
  where f 0 p0 e = run1 p0 e
        f t p0 e = let (mv, p1) = run1 p0 e
                   in mv `mseq` (Nothing, Auto $ f (t-1) p1)

        mseq Nothing  = id
        mseq (Just v) = seq v

-- | Drops the first n items
dropProc :: Int -> Proc a (Maybe a)
dropProc 0 = Auto $ \i -> (Just i, dropProc 0)
dropProc n = Auto $ const (Nothing, dropProc (n-1))

-- | Takes the first n items
takeProc :: Int -> Proc a (Maybe a)
takeProc 0 = Auto $ const (Nothing, takeProc 0)
takeProc n = Auto $ \i -> (Just i, takeProc (n-1))

-- | Count how many items this proc has seen
count :: (Integral b) => Proc a b
count = Auto (f 0)
  where f n _ = (n + 1, Auto $ f (n + 1))

-- | Uses an binary function to create a proc. Possible uses:
-- @
--   binary (+)
--   binary (-)
--   binary (max)
-- @
binary :: (a -> a -> a) -> Proc a a
binary f = Auto (\i -> (i, Auto $ g i))
  where g a b = let c = f a b
                in (c, Auto (g $ c))

-- | Uses a predicate to decide whether or not to return an
-- element. When this predicate evaluates to false, Nothing is
-- returned
select :: (a -> Bool) -> Proc a (Maybe a)
select p = Auto f
  where f i
          | p i       = (Just i, select p)
          | otherwise = (Nothing, select p)

-- | Sample @n@ elements out from a population of @m@ elements. For
-- every value, @n@ and @m@ are decremented. The function returns
-- @Nothing@ if @n == 0@ and the process starts over with the original
-- values when @m == 0@.
--
-- The frequency which elements are picked is defined by the following:
-- @
--   let L = total of elements
--       n = the number of elements to select
--       m = the population size
--   in n * (L `mod` m) + min n (L `mod` m))
-- @
sample :: Int  -- ^ Number of elements to select (@n@)
       -> Int  -- ^ Population size (@m@)
       -> Proc i (Maybe i)
sample n0 m0 = Auto (f n0 m0)
  where f _ 0 a       = (Just a, Auto $ f (n0-1) (m0-1))
        f n m a
          | n > 0     = (Just a, Auto $ f (n - 1) (m - 1))
          | otherwise = a `seq` (Nothing, Auto $ f 0 (m - 1))

-- | Invokes a given proc N number, keeping its intermediary
-- state. When N is reached, the proc is put back to its original
-- state and a value is produced.
window :: Int              -- ^ The number of elements to invoke proc
       -> Proc i o         -- ^ The proc to execute N number of times
       -> Proc i (Maybe o) -- ^ The resulting `window proc'
window n f0 = Auto (go (1, f0))
  where go (k, f) i = let (o, f1) = run1 f i
                      in if (k == n)
                         then (Just o, window n f0)
                         else o `seq` (Nothing, Auto $ go (k+1, f1))

