package main

import (
	"bufio"
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	"golang.org/x/exp/slices"
	"gopkg.in/yaml.v3"
)

func main() {
	var input string
	var assumeYes bool
	// load rule features
	prepareCmd := flag.NewFlagSet("prepare", flag.ExitOnError)
	prepareCmd.StringVar(&input, "input", "", "path to directory containing yaml rules")
	checkCmd := flag.NewFlagSet("check", flag.ExitOnError)
	checkCmd.BoolVar(&assumeYes, "yes", false, "do not prompt for choices, assume yes")

	switch os.Args[1] {
	case "prepare":
		err := prepareCmd.Parse(os.Args[2:])
		if err != nil {
			log.Fatalf("failed parsing input arguments")
		}
		if stat, err := os.Stat(input); err != nil || !stat.IsDir() {
			log.Fatal("invalid --input location, must point to directory containing rules")
		}
		allFeatures, err := loadRuleFeatures(input)
		if err != nil {
			log.Fatalf("failed to load features %v", err)
		}
		err = marshalYaml("rules.yaml", allFeatures)
		if err != nil {
			log.Fatalf("failed to write output %v", err)
		}
	case "check":
		err := checkCmd.Parse(os.Args[2:])
		if err != nil {
			log.Fatalf("failed parsing input arguments")
		}
		ruleFeatures := map[string][]RuleFeatures{}
		err = unmarshalYaml("rules.yaml", &ruleFeatures)
		if err != nil {
			log.Fatalf("failed unmarshaling features.yaml file %v", err)
		}
		ruleDiffs := []RuleDiff{}
		err = unmarshalYaml("diff.yaml", &ruleDiffs)
		if err != nil {
			ruleDiffs = make([]RuleDiff, 0)
		}
		defer func() {
			if err == nil {
				err = marshalYaml("diff.yaml", ruleDiffs)
				if err != nil {
					log.Fatalf("failed to write diff %v", err)
				}
			}
		}()
		canceled := false
		for path, features := range ruleFeatures {
			fmt.Printf("[*] Analyzing rules in %s\n", filepath.Base(path))
			for _, ruleFeature := range features {
				if !containsTemplate(ruleFeature.Description) {
					continue
				}
				// rate-limit
				if assumeYes {
					time.Sleep(3 * time.Second)
				}
				if slices.ContainsFunc[[]RuleDiff](ruleDiffs, func(rd RuleDiff) bool {
					return rd.Id == ruleFeature.Id
				}) {
					fmt.Printf("  ! Rule diff already generated for %s. Skipping...\n", ruleFeature.Id)
					continue
				}
				fmt.Printf("  ! Template found in rule %s\n", ruleFeature.Id)
				fmt.Printf("    > Previous Description: '%s'\n", ruleFeature.Description)
				fmt.Printf("      Update description? (Y - Yes, Enter - No, X - Stop) ")
				switch readInput(assumeYes) {
				case "Y":
					ruleContent, err := yaml.Marshal(&ruleFeature)
					if err != nil {
						continue
					}
					newDesc, err := suggestNewDescription(string(ruleContent), false)
					if err != nil {
						log.Printf("failed getting description for rule %s %v", newDesc, err)
						continue
					}
					fmt.Printf("    > Suggested Description: '%s'\n", newDesc)
					fmt.Printf("      Accept? (Y - Yes, Enter - No, X - Stop)")

					switch readInput(assumeYes) {
					case "Y":
						ruleDiffs = append(ruleDiffs,
							RuleDiff{
								Path: path,
								Id:   ruleFeature.Id,
								Description: Diff{
									From: ruleFeature.Description,
									To:   newDesc,
								},
							},
						)
					case "X":
						canceled = true
					}
				case "X":
					canceled = true
				}
				if canceled {
					break
				}
			}
			if canceled {
				break
			}
		}
	}
}

func containsTemplate(s string) bool {
	return strings.Contains(s, "{{") ||
		strings.Contains(s, "{")
}

func marshalYaml(path string, in interface{}) error {
	content, err := yaml.Marshal(&in)
	if err != nil {
		log.Fatalf("failed to marshal yaml %v", err)
	}
	return os.WriteFile(path, content, 0644)
}

func unmarshalYaml(path string, out interface{}) error {
	content, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	return yaml.Unmarshal(content, out)
}

func readInput(assumeYes bool) string {
	if assumeYes {
		fmt.Printf("\n")
		return "Y"
	} else {
		scanner := bufio.NewReader(os.Stdin)
		input, err := scanner.ReadString('\n')
		if err != nil {
			log.Printf("failed to read choice")
			return ""
		}
		input = strings.TrimSuffix(input, "\n")
		return input
	}
}
