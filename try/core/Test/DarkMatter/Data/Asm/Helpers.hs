{-# LANGUAGE OverloadedStrings #-}
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

module Test.DarkMatter.Data.Asm.Helpers where

import Data.Text (Text, pack, unpack)
import Test.QuickCheck
import DarkMatter.Data.Time
import DarkMatter.Data.Asm.Types
import DarkMatter.Data.Asm.Render

genPurge :: Gen Asm
genPurge = do { k <- fmap abs arbitrary
              ; return (Purge k)
              }

genWatch :: Gen Asm
genWatch = do { k     <- fmap abs arbitrary
              ; funcs <- arbitrary
              ; return (Watch k funcs)
              }

genThrow :: Gen Asm
genThrow = do { k <- fmap abs arbitrary
              ; c <- arbitrary
              ; v <- arbitrary
              ; return (Throw k c v)
              }

instance Arbitrary Asm where
  
  arbitrary = oneof [ genWatch
                    , genThrow
                    , genPurge
                    ]

instance Arbitrary Function where
  
  arbitrary = do { n <- fmap abs arbitrary
                 ; m <- fmap abs arbitrary
                 ; f <- arbitrary
                 ; elements [Window n m, Count, Truncate, Floor, Ceil, Round, Mean, Median, Minimum, Maximum, Abs, Arithmetic f]
                 }

instance Arbitrary Time where

  arbitrary = do { s <- fmap abs arbitrary
                 ; n <- fmap abs arbitrary
                 ; return (mktime s n)
                 }

instance Arbitrary ArithF where

  arbitrary = do { n <- arbitrary
                 ; elements [Mul n, Add n, Div n, Sub n]
                 }

instance Show Asm where
  
  show = unpack . render

instance Show Function where
  
  show = unpack . renderFunction